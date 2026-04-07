import urllib
import tempfile
import os.path
import numpy as np
import json
import math


def misc_plot_matplot(viz, env, args):
    try:
        import matplotlib.pyplot as plt
        plt.plot([1, 23, 2, 4])
        plt.ylabel('some numbers')
        viz.matplot(plt, env=env)
    except BaseException as err:
        print('Skipped matplotlib example')
        print('Error message: ', err)

# Example for Latex Support
def misc_plot_latex(viz, env, args):
    return viz.line(
        X=[1, 2, 3, 4],
        Y=[1, 4, 9, 16],
        name=r'$\alpha_{1c} = 352 \pm 11 \text{ km s}^{-1}$',
        opts={
            'showlegend': True,
            'title': "Demo Latex in Visdom",
            'xlabel': r'$\sqrt{(n_\text{c}(t|{T_\text{early}}))}$',
            'ylabel': r'$d, r \text{ (solar radius)}$',
        },
        env=env
    )

def misc_plot_latex_update(viz, env, args):
    win = misc_plot_latex(viz, env, args)
    viz.line(
        X=[1, 2, 3, 4],
        Y=[0.5, 2, 4.5, 8],
        win=win,
        name=r'$\beta_{1c} = 25 \pm 11 \text{ km s}^{-1}$',
        update='append',
        env=env
    )


def misc_video_tensor(viz, env, args):
    try:
        video = np.empty([256, 250, 250, 3], dtype=np.uint8)
        for n in range(256):
            video[n, :, :, :].fill(n)
        viz.video(tensor=video, env=env)
    except BaseException as e:
        print('Skipped video tensor example.' + str(e))


def misc_video_download(viz, env, args):
    try:
        # video demo:
        # download video from http://media.w3.org/2010/05/sintel/trailer.ogv
        video_url = 'http://media.w3.org/2010/05/sintel/trailer.ogv'
        videofile = os.path.join(tempfile.gettempdir(), 'trailer.ogv')
        urllib.request.urlretrieve(video_url, videofile)

        if os.path.isfile(videofile):
            viz.video(videofile=videofile, opts={'width': 864, 'height': 480}, env=env)
    except BaseException as e:
        print('Skipped video file example', e)


# audio demo:
def misc_audio_basic(viz, env, args):
    tensor = np.random.uniform(-1, 1, 441000)
    viz.audio(tensor=tensor, opts={'sample_frequency': 441000}, env=env)

# audio demo:
# download from http://www.externalharddrive.com/waves/animal/dolphin.wav
def misc_audio_download(viz, env, args):
    try:
        audio_url = 'http://www.externalharddrive.com/waves/animal/dolphin.wav'
        audiofile = os.path.join(tempfile.gettempdir(), 'dolphin.wav')
        urllib.request.urlretrieve(audio_url, audiofile)

        if os.path.isfile(audiofile):
            viz.audio(audiofile=audiofile, env=env)
    except BaseException:
        print('Skipped audio example')
 
# Arbitrary visdom content
def misc_arbitrary_visdom(viz, env, args):
    trace = dict(x=[1, 2, 3], y=[4, 5, 6], mode="markers+lines", type='custom',
                 marker={'color': 'red', 'symbol': 104, 'size': "10"},
                 text=["one", "two", "three"], name='1st Trace')
    layout = dict(title="First Plot", xaxis={'title': 'x1'},
                  yaxis={'title': 'x2'})

    viz._send({'data': [trace], 'layout': layout, 'win': 'mywin', 'eid': env})

# get/set state
def misc_getset_state(viz, env, args):
    window = viz.text('test one', env=env)
    data = json.loads(viz.get_window_data(window, env=env))
    data['content'] = 'test two'
    viz.set_window_data(json.dumps(data), env=env, win=window)


def _parse_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ('1', 'true', 'yes', 'y', 'on')


def misc_auto_logger(viz, env, args):
    """Auto logger example for loss and grad norm line plots."""
    steps = int(args[0]) if len(args) > 0 else 60
    use_torch = _parse_bool(args[1], default=False) if len(args) > 1 else False

    logger = viz.auto_logger(
        env=env,
        loss_title='AutoLogger Loss',
        grad_norm_title='AutoLogger Grad Norm',
    )

    if use_torch:
        try:
            import torch
            import torch.nn as nn

            torch.manual_seed(3)
            model = nn.Sequential(nn.Linear(16, 32), nn.ReLU(), nn.Linear(32, 1))
            optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
            criterion = nn.MSELoss()

            for step in range(steps):
                x = torch.randn(64, 16)
                y = x.sum(dim=1, keepdim=True) * 0.25

                optimizer.zero_grad()
                prediction = model(x)
                loss = criterion(prediction, y)
                loss.backward()

                grad_sq = 0.0
                for parameter in model.parameters():
                    if parameter.grad is not None:
                        grad_sq += float(parameter.grad.norm(2).item()) ** 2
                grad_norm = math.sqrt(grad_sq)

                if not logger.log(loss=float(loss.item()), grad_norm=grad_norm, step=step):
                    raise RuntimeError('Auto logger failed while plotting torch metrics')
                optimizer.step()

            return logger.loss_win
        except ImportError:
            print('PyTorch not found. Falling back to synthetic auto logger metrics.')

    rng = np.random.RandomState(7)
    for step in range(steps):
        loss = max(1e-6, np.exp(-step / 25.0) + 0.01 * rng.rand())
        grad_norm = max(1e-8, np.exp(-step / 30.0) + 0.04 * rng.rand())
        if not logger.log(loss=loss, grad_norm=grad_norm, step=step):
            raise RuntimeError('Auto logger failed while plotting synthetic metrics')

    return logger.loss_win


