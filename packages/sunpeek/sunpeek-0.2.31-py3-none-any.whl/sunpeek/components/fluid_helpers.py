import warnings

import numpy as np
from abc import ABC, abstractmethod
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV, ShuffleSplit
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as rt
import pandas as pd
import os


class ModelFactory():
    def __new__(cls, unit=None, onnx_file=None, onnx_model=None, onnx_model_bytes=None, is_pure=None):
        """Returns an instance of WPDModel, WPDModelPure or WPDModelMixed, depending on provided units.
        Parameters
        ----------
        unit : dict
            Units for inputs and outputs of the fluid model.
            Must have keys 'te' and 'out', optionally 'c' (then a WPDModelMixed is returned).
            Values must be valid pint unit strings.
        onnx_file : str
            Path to stored, trained ONNX file.

        Raises
        ------
        TypeError
            If unit is not a dict.
        KeyError
            If required keys 'te' and 'out' are not found, or dictionary has extra keys not 'te', 'c' or 'out'.
        """
        if not isinstance(unit, dict):
            raise TypeError('Parameter unit expected to be dictionary.')
        if len(unit) == 2:
            if set(unit.keys()) != {'te', 'out'}:
                raise KeyError('Keys "te" and "out" not in unit dict.')
        elif len(unit) == 3:
            if set(unit.keys()) != {'te', 'c', 'out'}:
                raise KeyError('Keys "te", "c" and "out" not in unit dict.')
        else:
            raise KeyError('Mismatched unit dict. Must have keys "te" and "out" and optionally "c" (for mixed fluids).')

        if len(unit) == 2 or is_pure:
            model = WPDModelPure(unit)
        else:
            model = WPDModelMixed(unit)

        if onnx_file is not None:
            model._onnx_file = onnx_file
        if onnx_model is not None:
            model.onnx_model = onnx_model.SerializeToString()
        if onnx_model_bytes is not None:
            model.onnx_model = onnx_model_bytes
        return model


class WPDModel(ABC):
    """
    Model for a particular property of a fluid, e.g. for density or for heat capacity.
    Has an ONNX filename and the units for all inputs (temperature, optionally concentration) and the calculated output.
    Can read WebPlotDigitizer csv files, train sklearn fit, save trained model as ONNX file and make predictions.
    Attributes
    ----------
    unit : dict
        Units for temperature ['te'], optionally concentration ['c'] and (mandatory) output property ['out'].
        Must be valid pint unit strings. These units are sent to the trained model if a prediction is required,
        and the prediction output is interpreted in unit['out'].
    _onnx_file : str
        Filename where trained sklearn is stored as an ONNX model.
    """

    _INPUT_NAME = 'wpd_input'

    def __init__(self, unit):
        self.unit = unit
        self._csv_file = None
        self._onnx_file = None
        self._df = None
        self.onnx_model = None

    @property
    def csv_file(self):
        if self._csv_file is None:
            raise TypeError('self._csv_file is None. You have to call train(csv_file).')
        return self._csv_file

    @property
    def onnx_file(self):
        if self._onnx_file is None:
            raise TypeError('self._onnx_file is None. You have to call train() before predict().')
        return self._onnx_file

    def train(self, csv_file, **kwargs):
        """
        Fits polynomial interpolation from WebPlotDigitizer exported csv data, returns fitted ONNX model.
        ONNX model is stored in same folder as csv_file and has same filename, but extension ".onnx"

        Parameters
        ----------
        csv_file : str
            WebPlotDigitizer export csv file. is expected to have multiple datasets, one for each concentration level.
        kwargs :
            Keyword arguments that will be passed to self.fit().

        Returns
        -------
        Filename where ONNX model was stored.
        """
        self._csv_file = csv_file
        self.csv2df()
        sk_model = self.fit(**kwargs)
        # self._onnx_file = self.sk2onnx(sk_model)
        onnx = convert_sklearn(sk_model, initial_types=self.sk_initial_type())
        self.onnx_model = onnx.SerializeToString()
        return self

    def fit(self, degree_range=None):
        """
        Polynomial interpolation with grid-search cross-validation of interpolation coefficients.
        Inspired by https://stackoverflow.com/questions/47442102/how-to-find-the-best-degree-of-polynomials

        Parameters
        ----------
        degree_range : int
            Miniumum and maximum polynomial degrees.

        Returns
        -------
        Trained sklearn model.
        """
        if degree_range is None:
            degree_range = np.arange(2, 4)  # default: quadratic or cubic polynomials
        # pipe = make_pipeline(PolynomialFeatures(), LinearRegression())

        # Spline & ridge regression: Would be an interesting option, but currently not convertible to onnx.
        # https://scikit-learn.org/stable/auto_examples/linear_model/plot_polynomial_interpolation.html#sphx-glr-auto-examples-linear-model-plot-polynomial-interpolation-py
        # pipeline example: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.SplineTransformer.html#sklearn.preprocessing.SplineTransformer

        # pipe = make_pipeline(StandardScaler(), PolynomialFeatures(), LinearRegression())
        # param_grid = {'polynomialfeatures__degree': degree_range}
        # # grid = GridSearchCV(pipe, param_grid, cv=20)
        # # grid = GridSearchCV(pipe, param_grid, cv=20, scoring='neg_mean_absolute_error')
        # # grid = GridSearchCV(pipe, param_grid, cv=LeaveOneOut(), scoring='neg_mean_absolute_error')
        # grid = GridSearchCV(pipe, param_grid, cv=ShuffleSplit(n_splits=10), scoring='neg_mean_absolute_error')

        pipe = make_pipeline(StandardScaler(), PolynomialFeatures(), Ridge(alpha=1e-3))
        param_grid = {'polynomialfeatures__degree': degree_range}
        # grid = GridSearchCV(pipe, param_grid, cv=20)
        # grid = GridSearchCV(pipe, param_grid, cv=20, scoring='neg_mean_absolute_error')
        # grid = GridSearchCV(pipe, param_grid, cv=LeaveOneOut(), scoring='neg_mean_absolute_error')
        grid = GridSearchCV(pipe, param_grid, cv=ShuffleSplit(n_splits=10), scoring='neg_mean_absolute_error')

        # # SplineTransformer not supported in ONNX conversion
        # pipe = make_pipeline(SplineTransformer(degree=3), Ridge(alpha=1e-3))
        # param_grid = {'splinetransformer__n_knots': np.arange(4,10)}
        # # grid = GridSearchCV(pipe, param_grid, cv=20)
        # # grid = GridSearchCV(pipe, param_grid, cv=20, scoring='neg_mean_absolute_error')
        # # grid = GridSearchCV(pipe, param_grid, cv=LeaveOneOut(), scoring='neg_mean_absolute_error')
        # grid = GridSearchCV(pipe, param_grid, cv=ShuffleSplit(n_splits=10), scoring='neg_mean_absolute_error')

        # X = self.df[['te', 'c']].to_numpy()
        X = self.get_X_df().to_numpy()
        y = self._df['out'].to_numpy()
        grid.fit(X, y)
        model = grid.best_estimator_
        return model

        # reg = model.named_steps['linearregression']
        # reg.get_params()
        # coefs = reg.coef_
        # intercept = reg.intercept_

    def sk2onnx(self, model):
        """
        Saves trained sklearn model as ONNX, with same filename as csv_file but .onnx extension.

        Notes
        -----
        Not all sklearn models are supported. For a reference of supported models, see
        https://onnx.ai/sklearn-onnx/supported.html

        Parameters
        ----------
        model :
        Trained sklearn model.

        Returns
        -------
        Filename where ONNX model was stored.
        """
        pre, ext = os.path.splitext(self.csv_file)
        onnx_file = pre + ".onnx"
        # Convert model into ONNX format
        onnx = convert_sklearn(model, initial_types=self.sk_initial_type())
        self.onnx_model = onnx.SerializeToString()
        with open(onnx_file, "wb") as f:
            f.write(onnx.SerializeToString())
        return onnx_file

    def sk_initial_type(self):
        initial_type = [(self._INPUT_NAME, FloatTensorType([None, self.n_inputs]))]
        return initial_type

    def predict(self, *args):
        """
        Compute model prediction with ONNX Runtime, based on self.onnx_file
        Parameters
        ----------
        args : pint Quantity
            Inputs required for prediciton: temperature and (optionally) concentration.
            Fluid temperature in unit self.unit['te']
            Fluid concentration in unit self.unit['c']

        Returns
        -------
        pint Quantity
        Calculated fluid property in unit self.unit['out']
        """
        # sess = rt.InferenceSession(self.onnx_file)
        sess = rt.InferenceSession(self.onnx_model)
        X = np.array(list(args)).transpose().reshape(-1, self.n_inputs).astype(np.float32)
        pred_onx = sess.run(['variable'], {self._INPUT_NAME: X})[0]
        return pred_onx.flatten()

    def is_trained(self):
        return self.onnx_model is not None

    @property
    @abstractmethod
    def n_inputs(self):
        pass

    @abstractmethod
    def get_X_df(self):
        pass

    @abstractmethod
    def csv2df(self):
        pass


class WPDModelPure(WPDModel):

    def csv2df(self):
        """Read WebPlotDigitizer csv with single dataset into dataframe.
        """
        df_csv = pd.read_csv(self.csv_file, header=0, sep=',')
        df_csv.rename(columns={'X': 'te', 'Y': 'out'}, inplace=True)
        self._df = df_csv

    @property
    def n_inputs(self):
        return 1

    def get_X_df(self):
        return self._df[['te']]

    def _plot_fit(self, type=None):   # pragma: no cover
        """Check quality of model fit, after calling self.train().
        Plots model fit and original / ground truth data from WebPlotDigitizer csv dataset.
        """
        try:
            import plotly.graph_objects as go
        except ModuleNotFoundError:
            warnings.warn('This function requires the plotly package, which is not installed. Install it with `pip install plotly`')
        N_POINTS = 50
        fig = go.Figure()
        te = np.linspace(self._df['te'].min() - 20, self._df['te'].max() + 20, N_POINTS)
        out = self.predict(te)
        fig.add_trace(go.Scatter(x=te, y=out,
                                 mode='lines',
                                 name='Model prediction'))
        # Measured values as scatter
        fig.add_trace(go.Scatter(x=self._df['te'], y=self._df['out'],
                                 mode='markers',
                                 marker=dict(
                                     color='Black',
                                     size=10,
                                     opacity=0.4,
                                     line=dict(
                                         color='Black',
                                         width=1
                                     )),
                                 name='WPD measurements'))

        if type == 'density':
            fig.update_layout(title='Density', width=1600, height=1200,
                              xaxis_title="Temperature [degC]", yaxis_title="Density [{self.unit['out']}]",
                              legend_traceorder="reversed")
        elif type == 'heat_capacity':
            fig.update_layout(title='Heat capacity', width=1600, height=1200,
                              xaxis_title="Temperature [degC]", yaxis_title=f"Heat capacity [{self.unit['out']}]",
                              legend_traceorder="reversed")
        else:
            raise ('type must be "density" or "heat_capacity"')
        fig.show()


class WPDModelMixed(WPDModel):

    def csv2df(self):
        """
        Read WebPlotDigitizer csv with multiple datasets, combine into single dataframe with added dataset level column.
        """
        df_csv = pd.read_csv(self.csv_file, header=[0, 1], sep=',')
        dataset_names = [c for c in df_csv.columns.get_level_values(0) if not c.startswith('Unnamed')]
        df = pd.DataFrame()
        for n in dataset_names:
            i = df_csv.columns.get_loc((n, 'X'))
            x = df_csv.iloc[:, i].dropna()
            y = df_csv.iloc[:, i + 1].dropna()
            c = pd.Series(float(n), index=x.index)
            df2 = pd.concat([x.rename('te'), y.rename('out'), c.rename('c')], axis=1)
            df = pd.concat([df, df2], ignore_index=True)
        self._df = df

    @property
    def n_inputs(self):
        return 2

    def get_X_df(self):
        return self._df[['te', 'c']]

    def _plot_fit(self, type=None):   # pragma: no cover
        """Check quality of model fit, after calling self.train().
        Plots model fit and original / ground truth data from WebPlotDigitizer csv dataset.
        """
        try:
            import plotly.graph_objects as go
        except ModuleNotFoundError:
            warnings.warn('This function requires the plotly package, which is not installed. Install it with `pip install plotly`')
        N_POINTS = 50
        # For all concentration levels, create output curves within measured temperature limits
        df = self._df.groupby('c').te.agg(['min', 'max'])
        fig = go.Figure()
        for i in np.arange(df.shape[0]):
            te = np.linspace(df.iloc[i, 0], df.iloc[i, 1], N_POINTS)
            c = df.index[i]
            c = np.full(te.shape, c)
            out = self.predict(te, c)
            fig.add_trace(go.Scatter(x=te, y=out,
                                     mode='lines',
                                     name=f"Model prediction, c={df.index[i]}%"))
        # Measured values as scatter
        fig.add_trace(go.Scatter(x=self._df['te'], y=self._df['out'],
                                 mode='markers',
                                 marker=dict(
                                     color='Black',
                                     size=10,
                                     opacity=0.4,
                                     line=dict(
                                         color='Black',
                                         width=1
                                     )),
                                 name='WPD measurements'))

        if type == 'density':
            fig.update_layout(title='Density', width=1600, height=1200,
                              xaxis_title="Temperature [degC]", yaxis_title="Density [{self.unit['out']}]",
                              legend_traceorder="reversed")
        elif type == 'heat_capacity':
            fig.update_layout(title='Heat capacity', width=1600, height=1200,
                              xaxis_title="Temperature [degC]", yaxis_title=f"Heat capacity [{self.unit['out']}]",
                              legend_traceorder="reversed")
        else:
            raise ('type must be "density" or "heat_capacity"')
        fig.show()
