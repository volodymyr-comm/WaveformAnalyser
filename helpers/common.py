import pandas as pd
import numpy as np


def plot_overlapping_charts_concept(data: pd.DataFrame, color='random'):
    axs = list()
    data.groupby(level=0, axis=0).apply(
        lambda x: axs.append(x.droplevel(0).plot(subplots=True,
                                                 legend=False,
                                                 style='-',
                                                 color=np.random.rand(3) if color == 'random' else color,
                                                 ax=axs[-1] if len(axs) else None),
                             )
    )
