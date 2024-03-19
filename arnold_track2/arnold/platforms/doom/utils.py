import numpy as np
import cv2


def process_buffers(game, params):
    """
    Process screen, depth and labels buffers.
    Resize the screen.
    """
    screen_buffer = game._screen_buffer
    depth_buffer = game._depth_buffer
    labels_buffer = game._labels_buffer
    labels = game._labels

    init_shape = screen_buffer.shape[-2:]
    all_buffers = []
    gray = params.gray
    height, width = params.height, params.width

    assert game.use_screen_buffer
    assert screen_buffer is not None
    assert screen_buffer.ndim == 3 and screen_buffer.shape[0] == 3
    assert not gray
    if screen_buffer.shape != (3, height, width):
        screen_buffer = cv2.resize(
            screen_buffer.transpose(1, 2, 0),
            (width, height),
            interpolation=cv2.INTER_AREA
        ).transpose(2, 0, 1)
    all_buffers.append(screen_buffer)

    assert not game.use_depth_buffer
    assert depth_buffer is None

    assert not game.use_labels_buffer
    assert game.use_game_features
    # assert labels_buffer is not None and labels is not None
    # assert labels_buffer.shape == init_shape

    # concatenate all buffers
    if len(all_buffers) == 1:
        return all_buffers[0], None
    else:
        return np.concatenate(all_buffers, 0), None


def get_n_feature_maps(params):
    """
    Return the number of feature maps.
    """
    n = 0
    if params.use_screen_buffer:
        n += 1 if params.gray else 3
    if params.use_depth_buffer:
        n += 1
    return n
