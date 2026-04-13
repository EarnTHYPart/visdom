/* eslint-env node */

const { spawn } = require('child_process');
const fs = require('fs');
const http = require('http');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const visdomPort = 8098;
const visdomUrl = `http://127.0.0.1:${visdomPort}/`;

function findPythonExecutable() {
  const windowsPython = path.join(repoRoot, '.venv', 'Scripts', 'python.exe');
  const posixPython = path.join(repoRoot, '.venv', 'bin', 'python');

  if (fs.existsSync(windowsPython)) {
    return windowsPython;
  }

  if (fs.existsSync(posixPython)) {
    return posixPython;
  }

  return process.platform === 'win32' ? 'python' : 'python3';
}

function waitForServer(url, timeoutMs = 120000) {
  const startedAt = Date.now();

  return new Promise((resolve, reject) => {
    const poll = () => {
      const request = http.get(url, (response) => {
        response.resume();
        if (response.statusCode && response.statusCode < 500) {
          resolve();
          return;
        }

        if (Date.now() - startedAt >= timeoutMs) {
          reject(new Error(`Timed out waiting for Visdom at ${url}`));
          return;
        }

        setTimeout(poll, 1000);
      });

      request.on('error', () => {
        if (Date.now() - startedAt >= timeoutMs) {
          reject(new Error(`Timed out waiting for Visdom at ${url}`));
          return;
        }

        setTimeout(poll, 1000);
      });
    };

    poll();
  });
}

function runCommand(command, args, env) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: repoRoot,
      env,
      shell: false,
      stdio: 'inherit',
    });

    child.on('error', reject);
    child.on('exit', (code) => {
      if (code === 0) {
        resolve();
        return;
      }

      reject(new Error(`${command} ${args.join(' ')} exited with code ${code}`));
    });
  });
}

async function main() {
  const pythonExecutable = findPythonExecutable();
  const pythonPath = path.resolve(repoRoot, 'py');
  const mergedPythonPath = process.env.PYTHONPATH
    ? `${pythonPath}${path.delimiter}${process.env.PYTHONPATH}`
    : pythonPath;
  const sharedEnv = {
    ...process.env,
    PYTHONPATH: mergedPythonPath,
    CYPRESS_VERIFY_TIMEOUT: process.env.CYPRESS_VERIFY_TIMEOUT || '120000',
  };

  const server = spawn(
    pythonExecutable,
    ['-m', 'visdom.server', '-port', String(visdomPort)],
    {
      cwd: repoRoot,
      env: sharedEnv,
      shell: false,
      stdio: 'inherit',
    }
  );

  let serverStopped = false;
  const stopServer = () => {
    if (serverStopped) {
      return;
    }

    serverStopped = true;
    if (!server.killed) {
      server.kill();
    }
  };

  process.on('SIGINT', () => {
    stopServer();
    process.exit(130);
  });

  process.on('SIGTERM', () => {
    stopServer();
    process.exit(143);
  });

  try {
    await waitForServer(visdomUrl);

    const cypressCommand = process.platform === 'win32' ? 'npx.cmd' : 'npx';
    const suites = [
      ['cypress', 'run', '--config', 'ignoreTestFiles=*.init.js'],
      ['cypress', 'run', '--spec', './cypress/integration/screenshots.init.js'],
      ['cypress', 'run', '--spec', './cypress/integration/screenshots.js'],
    ];

    const failures = [];

    for (const args of suites) {
      try {
        await runCommand(cypressCommand, args, sharedEnv);
      } catch (error) {
        failures.push(error.message);
      }
    }

    if (failures.length > 0) {
      console.error('\nE2E suite finished with failures:');
      failures.forEach((failure) => console.error(`- ${failure}`));
      process.exitCode = 1;
    }
  } finally {
    stopServer();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});