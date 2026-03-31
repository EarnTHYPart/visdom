/**
 * Copyright 2017-present, The Visdom Authors
 * All rights reserved.
 *
 * This source code is licensed under the license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import { useEffect, useRef } from 'react';

// custom hook to get previous value of a variable
function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

function parseQueryClauses(query) {
  if (!query || query.trim() === '') {
    return [];
  }

  const clauses = query
    .split(/\s+AND\s+/i)
    .map((part) => part.trim())
    .filter((part) => part.length > 0);

  let parsed = [];
  for (let i = 0; i < clauses.length; i++) {
    const match = clauses[i].match(/^([A-Za-z0-9_.-]+)\s*(=|>|<)\s*(.+)$/);
    if (!match) {
      return null;
    }

    parsed.push({
      key: match[1].toLowerCase(),
      op: match[2],
      value: match[3].trim(),
    });
  }

  return parsed;
}

function extractEnvParams(envName) {
  const params = {};
  const tokens = envName.split(/\s+|,|;|_(?=[A-Za-z0-9_.-]+=)/);
  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i].trim();
    const match = token.match(/^([A-Za-z0-9_.-]+)=(.+)$/);
    if (!match) {
      continue;
    }
    params[match[1].toLowerCase()] = match[2];
  }
  return params;
}

function compareValues(actual, expected, op) {
  if (op === '=') {
    return String(actual) === expected;
  }

  const a = Number(actual);
  const b = Number(expected);
  if (!Number.isFinite(a) || !Number.isFinite(b)) {
    return false;
  }

  if (op === '>') {
    return a > b;
  }
  if (op === '<') {
    return a < b;
  }
  return false;
}

function envMatchesQuery(envName, query) {
  const trimmed = (query || '').trim();
  if (trimmed === '') {
    return true;
  }

  const clauses = parseQueryClauses(trimmed);
  if (clauses === null) {
    return envName.toLowerCase().indexOf(trimmed.toLowerCase()) > -1;
  }

  const params = extractEnvParams(envName);
  for (let i = 0; i < clauses.length; i++) {
    const clause = clauses[i];
    if (!(clause.key in params)) {
      return false;
    }
    if (!compareValues(params[clause.key], clause.value, clause.op)) {
      return false;
    }
  }

  return true;
}

function filterEnvsByQuery(envList, query) {
  return envList.filter((env) => envMatchesQuery(env, query));
}

export { filterEnvsByQuery, usePrevious };
