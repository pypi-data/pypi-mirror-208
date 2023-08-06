import logging
import warnings
from functools import partial
from typing import (
    Any,
    Hashable,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

import numpy as np
import pandas as pd
import pandas.core.indexes.base as ibase
import xarray as xr
from xarray.core.utils import either_dict_or_kwargs

from genno.core.quantity import Quantity
from genno.core.types import Dims

log = logging.getLogger(__name__)


def _multiindex_of(obj: pd.Series):
    """Return ``obj.index``; if this is not a :class:`pandas.MultiIndex`, convert."""
    return (
        obj.index
        if isinstance(obj.index, pd.MultiIndex)
        else pd.MultiIndex.from_product([obj.index])
    )


class AttrSeries(pd.Series, Quantity):
    """:class:`pandas.Series` subclass imitating :class:`xarray.DataArray`.

    The AttrSeries class provides similar methods and behaviour to
    :class:`xarray.DataArray`, so that :mod:`genno.computations` functions and user
    code can use xarray-like syntax. In particular, this allows such code to be agnostic
    about the order of dimensions.

    Parameters
    ----------
    units : str or pint.Unit, optional
        Set the units attribute. The value is converted to :class:`pint.Unit` and added
        to `attrs`.
    attrs : :class:`~collections.abc.Mapping`, optional
        Set the :attr:`~pandas.Series.attrs` of the AttrSeries. This attribute was added
        in `pandas 1.0 <https://pandas.pydata.org/docs/whatsnew/v1.0.0.html>`_, but is
        not currently supported by the Series constructor.
    """

    # See https://pandas.pydata.org/docs/development/extending.html
    @property
    def _constructor(self):
        return AttrSeries

    def __init__(self, data=None, *args, name=None, attrs=None, **kwargs):
        attrs = Quantity._collect_attrs(data, attrs, kwargs)

        if isinstance(data, (pd.Series, xr.DataArray)):
            # Extract name from existing object or use the argument
            name = ibase.maybe_extract_name(name, data, type(self))

            try:
                # Pre-convert to pd.Series from xr.DataArray to preserve names and
                # labels. For AttrSeries, this is a no-op (see below).
                data = data.to_series()
            except AttributeError:
                # pd.Series
                pass
            except ValueError:
                # xr.DataArray
                if data.shape == tuple():
                    # data is a scalar/0-dimensional xr.DataArray. Pass the 1 value
                    data = data.data
                else:  # pragma: no cover
                    raise
            else:
                attrs.update()

        data, name = Quantity._single_column_df(data, name)

        if data is None:
            kwargs["dtype"] = float

        # Don't pass attrs to pd.Series constructor; it currently does not accept them
        pd.Series.__init__(self, data, *args, name=name, **kwargs)

        # Update the attrs after initialization
        self.attrs.update(attrs)

    def __repr__(self):
        return super().__repr__() + f", units: {self.units}"

    @classmethod
    def from_series(cls, series, sparse=None):
        """Like :meth:`xarray.DataArray.from_series`."""
        return AttrSeries(series)

    def assign_coords(self, coords=None, **coord_kwargs):
        """Like :meth:`xarray.DataArray.assign_coords`."""
        coords = either_dict_or_kwargs(coords, coord_kwargs, "assign_coords")

        idx = _multiindex_of(self)

        # Construct a new index
        new_idx = idx.copy()
        for dim, values in coords.items():
            expected_len = len(idx.levels[idx.names.index(dim)])
            if expected_len != len(values):
                raise ValueError(
                    f"conflicting sizes for dimension {repr(dim)}: length "
                    f"{expected_len} on <this-array> and length {len(values)} on "
                    f"{repr(dim)}"
                )

            new_idx = new_idx.set_levels(values, level=dim)

        # Return a new object with the new index
        return self.set_axis(new_idx)

    def bfill(self, dim: Hashable, limit: Optional[int] = None):
        """Like :meth:`xarray.DataArray.bfill`."""
        # TODO this likely does not work for 1-D quantities due to unstack(); test and
        #      if needed use _maybe_groupby()
        return self._replace(
            self.unstack(dim)
            .fillna(method="bfill", axis=1, limit=limit)
            .stack()
            .reorder_levels(self.dims),
        )

    @property
    def coords(self):
        """Like :attr:`xarray.DataArray.coords`. Read-only."""
        levels = (
            self.index.levels
            if isinstance(self.index, pd.MultiIndex)
            else [self.index.values]
        )
        return xr.Dataset(None, coords=dict(zip(self.index.names, levels))).coords

    def cumprod(self, dim=None, axis=None, skipna=None, **kwargs):
        """Like :meth:`xarray.DataArray.cumprod`."""
        if axis:
            log.info(f"{self.__class__.__name__}.cumprod(…, axis=…) is ignored")
        if skipna is None:
            skipna = self.dtype == float
        if dim in (None, "..."):
            dim = self.dims

        # Group on dimensions other than `dim`
        result = self._maybe_groupby(dim).cumprod(skipna=skipna, **kwargs)
        return self._replace(result)

    @property
    def dims(self) -> Tuple[Hashable, ...]:
        """Like :attr:`xarray.DataArray.dims`."""
        return tuple(filter(None, self.index.names))

    @property
    def shape(self) -> Tuple[int, ...]:
        """Like :attr:`xarray.DataArray.shape`."""
        idx = _multiindex_of(self).remove_unused_levels()
        return tuple(len(idx.levels[i]) for i in map(idx.names.index, self.dims))

    def drop(self, label):
        """Like :meth:`xarray.DataArray.drop`."""
        return self.droplevel(label)

    def drop_vars(
        self, names: Union[Hashable, Iterable[Hashable]], *, errors: str = "raise"
    ):
        """Like :meth:`xarray.DataArray.drop_vars`."""

        return self.droplevel(names)

    def expand_dims(self, dim=None, axis=None, **dim_kwargs: Any) -> "AttrSeries":
        """Like :meth:`xarray.DataArray.expand_dims`."""
        dim = either_dict_or_kwargs(dim, dim_kwargs, "expand_dims")
        if axis is not None:
            raise NotImplementedError  # pragma: no cover

        result = self
        for name, values in reversed(list(dim.items())):
            N = len(values)
            if N == 0:  # Dimension without labels
                N, values = 1, [None]
            result = pd.concat([result] * N, keys=values, names=[name])

        return result

    def ffill(self, dim: Hashable, limit: Optional[int] = None):
        """Like :meth:`xarray.DataArray.ffill`."""
        # TODO this likely does not work for 1-D quantities due to unstack(); test and
        #      if needed use _maybe_groupby()
        return self._replace(
            self.unstack(dim)
            .fillna(method="ffill", axis=1, limit=limit)
            .stack()
            .reorder_levels(self.dims),
        )

    def item(self, *args):
        """Like :meth:`xarray.DataArray.item`."""
        if len(args) and args != (None,):
            raise NotImplementedError
        elif self.size != 1:
            raise ValueError
        return self.iloc[0]

    def interp(
        self,
        coords: Optional[Mapping[Hashable, Any]] = None,
        method: str = "linear",
        assume_sorted: bool = True,
        kwargs: Optional[Mapping[str, Any]] = None,
        **coords_kwargs: Any,
    ):
        """Like :meth:`xarray.DataArray.interp`.

        This method works around two long-standing bugs in :mod:`pandas`:

        - `pandas-dev/pandas#25460 <https://github.com/pandas-dev/pandas/issues/25460>`_
        - `pandas-dev/pandas#31949 <https://github.com/pandas-dev/pandas/issues/31949>`_
        """
        from scipy.interpolate import interp1d

        if kwargs is None:
            kwargs = {}

        coords = either_dict_or_kwargs(coords, coords_kwargs, "interp")
        if len(coords) > 1:
            raise NotImplementedError("interp() on more than 1 dimension")

        # Unpack the dimension and levels (possibly overlapping with existing)
        dim = list(coords.keys())[0]
        levels = coords[dim]
        # Ensure a list
        if isinstance(levels, (int, float)):
            levels = [levels]

        # Preserve order of dimensions
        dims = self.dims

        # Dimension other than `dim`
        other_dims = list(filter(lambda d: d != dim, dims))

        def join(base, item):
            """Rejoin a full key for the MultiIndex in the correct order."""
            # Wrap a scalar `base` (only occurs with len(other_dims) == 1; pandas < 2.0)
            base = list(base) if isinstance(base, tuple) else [base]
            return [
                (base[other_dims.index(d)] if d in other_dims else item) for d in dims
            ]

        # Group by `dim` so that each level appears ≤ 1 time in `group_series`
        result = []
        groups = self.groupby(other_dims) if len(other_dims) else [(None, self)]
        for group_key, group_series in groups:
            # Work around https://github.com/pandas-dev/pandas/issues/25460; can't do:
            # group_series.reindex(…, level=dim)

            # A 1-D index for `dim` with the union of existing and new coords
            idx = pd.Index(
                sorted(set(group_series.index.get_level_values(dim)).union(levels))
            )

            # Reassemble full MultiIndex with the new coords added along `dim`
            full_idx = pd.MultiIndex.from_tuples(
                map(partial(join, group_key), idx), names=dims
            )

            # - Reindex to insert NaNs
            # - Replace the full index with the 1-D index
            s = group_series.reindex(full_idx).set_axis(idx)

            # Work around https://github.com/pandas-dev/pandas/issues/31949
            # Location of existing values
            x = s.notna()

            # - Create an interpolator from the non-NaN values.
            # - Apply it to the missing indices.
            # - Reconstruct a Series with these indices.
            # - Use this Series to fill the NaNs in `s`.
            # - Restore the full MultiIndex.
            result.append(
                s.fillna(
                    pd.Series(
                        interp1d(s[x].index, s[x], kind=method, **kwargs)(s[~x].index),
                        index=s[~x].index,
                    )
                ).set_axis(full_idx)
            )

        # - Restore dimension order and attributes.
        # - Select only the desired `coords`.
        return self._replace(pd.concat(result).reorder_levels(dims)).sel(coords)

    def rename(
        self,
        new_name_or_name_dict: Union[Hashable, Mapping[Hashable, Hashable]] = None,
        **names: Hashable,
    ):
        """Like :meth:`xarray.DataArray.rename`."""
        if new_name_or_name_dict is None or isinstance(new_name_or_name_dict, Mapping):
            index = either_dict_or_kwargs(new_name_or_name_dict, names, "rename")
            return self.rename_axis(index=index)
        else:
            assert 0 == len(names)
            return super().rename(new_name_or_name_dict)

    def sel(
        self,
        indexers: Optional[Mapping[Any, Any]] = None,
        method: Optional[str] = None,
        tolerance=None,
        drop: bool = False,
        **indexers_kwargs: Any,
    ):
        """Like :meth:`xarray.DataArray.sel`."""
        if method is not None:
            raise NotImplementedError(f"AttrSeries.sel(…, method={method!r})")
        if tolerance is not None:
            raise NotImplementedError(f"AttrSeries.sel(…, tolerance={tolerance!r})")

        indexers = either_dict_or_kwargs(indexers, indexers_kwargs, "sel")

        if len(indexers) == 1:
            level, key = list(indexers.items())[0]
            if isinstance(key, str) and not drop:
                if isinstance(self.index, pd.MultiIndex):
                    # When using .loc[] to select 1 label on 1 level, pandas drops the
                    # level. Use .xs() to avoid this behaviour unless drop=True
                    return AttrSeries(self.xs(key, level=level, drop_level=False))
                else:
                    # No MultiIndex; use .loc with a slice to avoid returning scalar
                    return self.loc[slice(key, key)]

        if len(indexers) and all(
            isinstance(i, xr.DataArray) for i in indexers.values()
        ):
            # DataArray indexers

            # Combine indexers in a data set; dimensions are aligned
            ds = xr.Dataset(indexers)

            # All dimensions indexed
            dims_indexed = set(indexers.keys())
            # Dimensions to discard
            dims_drop = set(ds.data_vars.keys())

            # Check contents of indexers
            if any(ds.isnull().any().values()):
                raise IndexError(
                    f"Dimensions of indexers mismatch: {ds.notnull().sum()}"
                )
            elif len(ds.dims) > 1:
                raise NotImplementedError(  # pragma: no cover
                    f"map to > 1 dimensions {repr(ds.dims)} with AttrSeries.sel()"
                )

            # pd.Index object with names and levels of the new dimension to be created
            idx = ds.coords.to_index()

            # Dimensions to drop on sliced data to avoid duplicated dimensions
            drop_slice = list(dims_indexed - dims_drop)

            # Dictionary of Series to concatenate
            series = {}

            # Iterate over labels in the new dimension
            for label in idx:
                # Get a slice from the indexers corresponding to this label
                loc_ds = ds.sel({idx.name: label})

                # Assemble a key with one element for each dimension
                seq0 = [loc_ds.get(d) for d in self.dims]
                # Replace None from .get() with slice(None) or unpack a single value
                seq1 = [slice(None) if item is None else item.item() for item in seq0]

                # Use the key to retrieve 1+ integer locations; slice; store
                series[label] = self.iloc[self.index.get_locs(seq1)].droplevel(
                    drop_slice
                )

            # Rejoin to a single data frame; drop the source levels
            data = pd.concat(series, names=[idx.name]).droplevel(list(dims_drop))
        else:
            # Other indexers

            # Iterate over dimensions
            idx = []
            to_drop = set()
            for dim in self.dims:
                # Get an indexer for this dimension
                i = indexers.get(dim, slice(None))

                if np.isscalar(i) and drop:
                    to_drop.add(dim)

                # Maybe unpack an xarray DataArray indexers, for pandas
                idx.append(i.data if isinstance(i, xr.DataArray) else i)

            # Silence a warning from pandas ≥1.4 that may be spurious
            # FIXME investigate, adjust the code, remove the filter
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    ".*indexing on a MultiIndex with a nested sequence.*",
                    FutureWarning,
                )
                # Select
                data = self.loc[tuple(idx)]

            # Only drop if not returning a scalar value
            if isinstance(data, pd.Series):
                # Drop levels where a single value was selected
                data = data.droplevel(list(to_drop & set(data.index.names)))

        # Return
        return self._replace(data)

    def shift(
        self,
        shifts: Optional[Mapping[Hashable, int]] = None,
        fill_value: Any = None,
        **shifts_kwargs: int,
    ):
        """Like :meth:`xarray.DataArray.shift`."""
        shifts = either_dict_or_kwargs(shifts, shifts_kwargs, "shift")

        result = self
        for dim, periods in shifts.items():
            result = result._maybe_groupby(dim).shift(
                periods=periods, fill_value=fill_value
            )
        return self._replace(result)

    def sum(
        self,
        dim: Dims = None,
        # Signature from xarray.DataArray
        # *,
        skipna: Optional[bool] = None,
        min_count: Optional[int] = None,
        keep_attrs: Optional[bool] = None,
        **kwargs: Any,
    ) -> "AttrSeries":
        """Like :meth:`xarray.DataArray.sum`."""
        if skipna is not None or min_count is not None:
            raise NotImplementedError

        if dim is None or isinstance(dim, Hashable):
            dim = tuple(filter(None, (dim,)))

        # Check dimensions
        bad_dims = set(dim) - set(self.index.names)
        if bad_dims:
            raise ValueError(
                f"{bad_dims} not found in array dimensions {self.index.names}"
            )

        # Create the object on which to .sum()
        return self._replace(self._maybe_groupby(dim).sum(**kwargs))

    def squeeze(self, dim=None, *args, **kwargs):
        """Like :meth:`xarray.DataArray.squeeze`."""
        assert kwargs.pop("drop", True)

        try:
            idx = self.index.remove_unused_levels()
        except AttributeError:
            return self

        to_drop = []
        for i, name in enumerate(idx.names):
            if dim and name != dim:
                continue
            elif len(idx.levels[i]) > 1:
                if dim is None:
                    continue
                else:
                    raise ValueError(
                        "cannot select a dimension to squeeze out which has length "
                        "greater than one"
                    )

            to_drop.append(name)

        if dim and not to_drop:
            # Specified dimension does not exist
            raise KeyError(dim)

        return self.droplevel(to_drop)

    def transpose(self, *dims):
        """Like :meth:`xarray.DataArray.transpose`."""
        return self.reorder_levels(dims)

    def to_dataframe(
        self,
        name: Optional[Hashable] = None,
        dim_order: Optional[Sequence[Hashable]] = None,
    ) -> pd.DataFrame:
        """Like :meth:`xarray.DataArray.to_dataframe`."""
        if dim_order is not None:
            raise NotImplementedError("dim_order arg to to_dataframe()")

        self.name = name or self.name or "value"  # type: ignore
        return self.to_frame()

    def to_series(self):
        """Like :meth:`xarray.DataArray.to_series`."""
        return self

    # Internal methods

    def align_levels(self, other):
        """Return a copy of `self` with common levels in the same order as `other`.

        Work-around for https://github.com/pandas-dev/pandas/issues/25760.
        """
        # TODO test for possible removal, since the upstream bug appears closed

        # If other.index is a (1D) Index object, convert to a MultiIndex with 1 level so
        # .levels[…] can be used, below. See also Quantity._single_column_df()
        other_index = _multiindex_of(other)

        # other.index.names, excluding 'None'
        other_names = list(filter(None, other_index.names))

        # Lists of common dimensions, and dimensions on `other` missing from `self`.
        common, missing = [], []
        for i, n in enumerate(other_names):
            if n in self.index.names:
                common.append(n)
            else:
                missing.append((i, n))

        result = self
        if len(common) == 0:
            # No common dimensions
            if len(missing):
                # Broadcast over missing dimensions
                result = result.expand_dims(
                    {dim: other_index.levels[i] for i, dim in missing}
                )

            if len(self) == len(self.index.names) == 1 and len(result.dims) > 0:
                # concat() of scalars (= length-1 pd.Series) results in an innermost
                # index level filled with int(0); discard this
                result = result.droplevel(-1)

            # Reordering starts with the dimensions of `other`
            order = other_names
        else:
            # Some common dimensions exist; no need to broadcast, only reorder
            order = common

        # Append the dimensions of `self`
        order.extend(
            filter(lambda n: n is not None and n not in other_names, self.index.names)
        )

        # Reorder, if that would do anything
        return result.reorder_levels(order) if len(order) > 1 else result

    def _maybe_groupby(self, dim):
        """Return an object for operations along dimension(s) `dim`.

        If `dim` is a subset of :attr:`dims`, returns a SeriesGroupBy object along the
        other dimensions.
        """
        if len(set(dim)) in (0, len(self.index.names)):
            return cast(pd.Series, super())
        else:
            # Group on dimensions other than `dim`
            return self.groupby(
                list(filter(lambda d: d not in dim, self.index.names)),  # type: ignore
                observed=True,
            )

    def _replace(self, data) -> "AttrSeries":
        """Shorthand to preserve attrs."""
        return self.__class__(data, name=self.name, attrs=self.attrs)
