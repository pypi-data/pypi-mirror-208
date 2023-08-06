import numpy as np
import slideflow as sf
from os.path import join
from slideflow import log

from .mosaic import MosaicWidget
from ..utils import EasyDict

#----------------------------------------------------------------------------

class ExperimentalMosaicWidget(MosaicWidget):
    """Experimental design with additional functionality (under development)."""

    def load_model_and_umap(self, model_path, umap_path, layers='postconv'):
        self.load_umap(umap_path)
        features_model, input_tensor = self._build_feature_generator(model_path, layers=layers)
        self.viz._umap_encoders = self._load_umap_encoder(umap_path, features_model, input_tensor)
        self.viz._async_renderer._umap_encoders = self.viz._umap_encoders
        log.info(f"Loaded UMAP encoder at [green]{umap_path}[/]")

    def _load_umap_encoder(self, path, feature_model, input_tensor=None):
        """Assumes `feature_model` has two outputs: (features, logits)"""
        import tensorflow as tf

        encoder = tf.keras.models.load_model(join(path, 'encoder'))
        encoder._name = f'umap_encoder'
        outputs = [encoder(feature_model.outputs[0])]

        # Add the logits output
        outputs += [feature_model.outputs[-1]]

        # Build the encoder model for all layers
        encoder_model = tf.keras.models.Model(
            inputs=input_tensor if input_tensor is not None else feature_model.input,
            outputs=outputs
        )
        return EasyDict(
            encoder=encoder_model,
            layers=['mosaic_umap'],
            range={'mosaic_umap': np.load(join(path, 'range_clip.npz'))['range']},
            clip={'mosaic_umap': np.load(join(path, 'range_clip.npz'))['clip']}
        )

    def _build_feature_generator(self, path, layers='postconv', **kwargs):
        is_simclr = sf.util.is_simclr_model_path(path)
        if is_simclr:
            import tensorflow as tf
            from slideflow import simclr
            model = simclr.load(path)
            simclr_args = simclr.load_model_args(path)
            input_shape = (simclr_args.image_size, simclr_args.image_size, 3)
            inp = tf.keras.layers.InputLayer(input_shape=input_shape, name='input')
            input_tensor = inp.input
            model.outputs = model(inp.output, training=False)
        else:
            model = sf.model.Features(path, layers=layers, include_preds=True, **kwargs).model
            input_tensor = None
        return model, input_tensor

    def render(self):
        self.viz.args.use_umap_encoders = self.coords is not None
        super().render()