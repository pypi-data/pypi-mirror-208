# This file is part of addict-tracking-changes
#
# Copyright (c) [2023] by Webworks, MonalLabs.
# This file is released under the MIT License.
#
# Author(s): webworks@MonalLabs

# MIT License

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



import copy
import pickle
import tempfile
from collections import namedtuple
from pathlib import Path

from addict_tracking_changes import Dict
from addict_tracking_changes import walker as dictWalker
from dpath import delete as ddelete
from dpath import new as dnew
from dpath import set as dset
import pytest


def func(x):
    return x + 1


TEST_VAL = [1, 2, 3]
TEST_DICT = {"a": {"b": {"c": TEST_VAL}}}


@pytest.fixture
def prop():
    return Dict()


@pytest.fixture
def trackerprop():
    return Dict(track_changes=True)


@pytest.fixture
def populated_trackerprop():
    mydict = Dict(track_changes=True)
    mydict.a.b = 1
    mydict.a.c = 1
    mydict.x = "4"
    return mydict


@pytest.fixture
def freezed_populated_trackerprop(populated_trackerprop):
    populated_trackerprop.freeze()
    return populated_trackerprop


@pytest.fixture
def dict():
    return Dict


class TestBasicDictOps:
    def test_set_one_level_item(self, prop):
        some_dict = {"a": TEST_VAL}
        prop["a"] = TEST_VAL
        assert prop == some_dict

    def test_set_two_level_items(self, prop):
        some_dict = {"a": {"b": TEST_VAL}}
        prop["a"]["b"] = TEST_VAL
        assert prop == some_dict

    def test_set_three_level_items(self, prop):
        prop["a"]["b"]["c"] = TEST_VAL
        assert prop == TEST_DICT

    def test_set_one_level_property(self, prop):
        prop.a = TEST_VAL
        assert prop == {"a": TEST_VAL}

    def test_set_two_level_properties(self, prop):
        prop.a.b = TEST_VAL
        assert prop == {"a": {"b": TEST_VAL}}

    def test_set_three_level_properties(self, prop):
        prop.a.b.c = TEST_VAL
        assert prop == TEST_DICT

    def test_init_with_dict(self, prop):
        assert TEST_DICT == Dict(TEST_DICT)

    def test_init_with_kws(self):
        # TODO: how to use fixtures here:
        prop = Dict(a=2, b={"a": 2}, c=[{"a": 2}])
        assert prop == {"a": 2, "b": {"a": 2}, "c": [{"a": 2}]}

    def test_init_with_tuples(self, dict):
        prop = dict((0, 1), (1, 2), (2, 3))
        assert prop == {0: 1, 1: 2, 2: 3}

    def test_init_with_list(self, dict):
        prop = dict([(0, 1), (1, 2), (2, 3)])
        assert prop == {0: 1, 1: 2, 2: 3}

    def test_init_with_generator(self, dict):
        prop = dict(((i, i + 1) for i in range(3)))
        assert prop == {0: 1, 1: 2, 2: 3}

    def test_init_with_tuples_and_empty_list(self, dict):
        prop = dict((0, 1), [], (2, 3))
        assert prop == {0: 1, 2: 3}


class TestTracking:
    def test_has_track_changes_attr(self, trackerprop):
        assert getattr(trackerprop, "__track_changes") == True

    def test_with_one_level_item(self, trackerprop):
        trackerprop["a"] = 1
        assert list(trackerprop.get_changed_history()) == ["/a"]

    def test_with_one_level_two_item(self, trackerprop):
        trackerprop["a"] = 3
        trackerprop["g"] = 5
        assert list(trackerprop.get_changed_history()) == ["/a", "/g"]

    def test_with_two_level_two_item(self, trackerprop):
        trackerprop.a.b = 3
        trackerprop.a.c = 5
        assert list(trackerprop.get_changed_history()) == ["/a/b", "/a/c"]

    def test_with_two_level_two_list_item(self, trackerprop):
        trackerprop.a.b = [1, [1]]
        trackerprop.a.c = [2, [2, [3]]]
        assert list(trackerprop.get_changed_history()) == [
            "/a/b/0",
            "/a/b/1/0",
            "/a/c/0",
            "/a/c/1/0",
            "/a/c/1/1/0",
        ]

    def test_with_two_level_list_dict_item(self, trackerprop):
        """
        within the list there is dict
        """
        x1 = Dict(track_changes=True)
        x2 = Dict(track_changes=True)

        x1.x.a = 1
        x2.y.z = 4
        trackerprop.a.b = [1, x1]
        trackerprop.a.c = [2, x2]
        assert list(trackerprop.get_changed_history()) == [
            "/a/b/0",
            "/a/b/1/x/a",
            "/a/c/0",
            "/a/c/1/y/z",
        ]

    def test_with_two_level_two_dict_item(self, trackerprop):
        trackerprop.a.b = {"a": 1}
        trackerprop.a.c = {"b": 2}

        assert list(trackerprop.get_changed_history()) == [
            "/a/b",
            "/a/c",
        ]

    def test_with_two_level_two_tuple_item(self, trackerprop):
        trackerprop.a.b = ("a", "b")
        trackerprop.a.c = ("a", "c")
        assert list(trackerprop.get_changed_history()) == [
            "/a/b",
            "/a/c",
        ]

    def test_multiple_rounds_of_set_clear_history(self, trackerprop):
        for _i in range(5):
            trackerprop.a.b = 1
            trackerprop.c.d = 1
            trackerprop.clear_changed_history()

        trackerprop.a.b = 1
        trackerprop.c.d = 1

        assert list(trackerprop.get_changed_history()) == [
            "/a/b",
            "/c/d",
        ]

        pass

    def test_clear_changed_history(self, populated_trackerprop):
        populated_trackerprop.clear_changed_history()
        assert list(populated_trackerprop.get_changed_history()) == []

    def test_clear_changed_history_list(self, trackerprop):
        trackerprop.a.b = [1, [1]]
        trackerprop.a.c = [2, [2, [3]]]
        trackerprop.clear_changed_history()
        assert list(trackerprop.get_changed_history()) == []

    def test_clear_changed_history_dict(self, trackerprop):
        trackerprop.a.b = {"a": 1}
        trackerprop.a.c = {"b": 1}
        trackerprop.clear_changed_history()
        assert list(trackerprop.get_changed_history()) == []

    def test_clear_changed_history_tuple(self, trackerprop):
        trackerprop.a.b = (1, 2)
        trackerprop.a.c = (1, 2)
        trackerprop.clear_changed_history()
        assert list(trackerprop.get_changed_history()) == []

    def test_clear_changed_history_with_two_level_list_dict_item(self, trackerprop):
        """
        within the list there is dict
        """
        x1 = Dict(track_changes=True)
        x2 = Dict(track_changes=True)

        x1.x.a = 1
        x2.y.z = 4
        trackerprop.a.b = [1, x1]
        trackerprop.a.c = [2, x2]
        trackerprop.clear_changed_history()
        assert list(trackerprop.get_changed_history()) == []

    def test_to_dict(self, trackerprop):
        trackerprop.a.b = {"a": 1}
        trackerprop.a.c = {"b": 1}
        trackerprop.a.x = [1, [1]]
        trackerprop.a.y = [2, [2, [3]]]
        x1 = Dict(track_changes=True)
        x2 = Dict(track_changes=True)

        x1.r.a = 1
        x2.r.z = 4
        trackerprop.a.d1 = [1, x1]
        trackerprop.a.d2 = [2, x2]
        assert trackerprop.to_dict() == Dict(
            {
                "a": {
                    "b": {"a": 1},
                    "c": {"b": 1},
                    "x": [1, [1]],
                    "y": [2, [2, [3]]],
                    "d1": [1, {"r": {"a": 1}}],
                    "d2": [2, {"r": {"z": 4}}],
                }
            }
        )


class TestMisc:
    def test_walker(self, populated_trackerprop):
        assert {("/a/b", 1), ("/x", "4"), ("/a/c", 1)} == {
            _ for _ in dictWalker(populated_trackerprop)
        }

    def test_walker_with_guards(self, populated_trackerprop):
        res = {
            (_[0], frozenset(_[1]))
            for _ in dictWalker(populated_trackerprop, guards=["/a"])
        }  #
        assert {("/x", frozenset({"4"})), ("/a", frozenset({"b", "c"}))} == res

    def test_modify_frozen(self, populated_trackerprop):
        """
        try to modify a nested
        """
        populated_trackerprop.freeze()
        with pytest.raises(KeyError) as excinfo:
            populated_trackerprop.z = 5
        assert "z" in str(excinfo.value)

    def test_modify_nested_frozen(self, populated_trackerprop):
        """
        freeze and modify a nested key. Check to see if frozen is
        not superficial.
        """
        populated_trackerprop.r.nested_key = Dict()
        populated_trackerprop.freeze()
        with pytest.raises(KeyError) as excinfo:
            populated_trackerprop.r.nested_key.dd = 5

        assert "dd" in str(excinfo.value)

    def test_unfreeze(self, freezed_populated_trackerprop):
        freezed_populated_trackerprop.unfreeze()
        freezed_populated_trackerprop.kk = 5
        assert freezed_populated_trackerprop.kk == 5

    # def test_delete_attr(self, populated_trackerprop):
    #     pass

    def test_pickle(self, populated_trackerprop):
        """
        test if
        1. pickle/unpickle of addict is working
        2. set tracker on unpickled object
        3. test get_changed_history, set_changed_history on unpickled object
        """
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            # print(f"Temporary file created: {temp_file.name}")
            path = Path(temp_file.name)
            with path.open("wb") as fh:
                pickle.dump(populated_trackerprop, fh)

            with path.open("rb") as fh:
                dict_loaded = pickle.load(fh)

        assert [_ for _ in dictWalker(populated_trackerprop)] == [
            _ for _ in dictWalker(dict_loaded)
        ]
        dict_loaded.set_tracker(track_changes=True)
        assert [_ for _ in dict_loaded.get_changed_history()] == []
        dict_loaded.z.a = 1
        assert [_ for _ in dict_loaded.get_changed_history()] == ["/z/a"]
        dict_loaded.clear_changed_history()

        assert [_ for _ in dict_loaded.get_changed_history()] == []

    def test_changed_history_on_untracked_dict(self):
        mydict = Dict(track_changes=False)
        mydict.a = 1
        mydict.b.c.d = 2
        # print (mydict)
        mydict.clear_changed_history()
        assert list(mydict.get_changed_history()) == []

    def test_del_tracked_attribute(self, trackerprop):
        trackerprop.a.b = 1
        trackerprop.c.d.e = 1
        del trackerprop["c"]
        assert [_ for _ in trackerprop.get_changed_history()] == ["/a/b"]

        del trackerprop["a"]["b"]
        assert [_ for _ in trackerprop.get_changed_history()] == []

        trackerprop.a.b = 1

        assert [_ for _ in trackerprop.get_changed_history()] == ["/a/b"]

    def test_opaque_dist(self, trackerprop):
        valdict = {"a": 1}
        fields = valdict.keys()
        tpl_cls = namedtuple("anon", fields)
        value = tpl_cls(*valdict.values())

        trackerprop.okey = value
        assert [_ for _ in trackerprop.get_changed_history()] == ["/okey"]

    def test_initialization_non_dict(self):
        """
        namedtuple is treated as namedtuple and not as a dict.
        """
        Point = namedtuple("Point", "x y")
        mydict = Dict({"x": {"y": Point(1, 2)}}, track_changes=False)
        assert mydict.x.y == Point(1, 2)

    def test_shallow_copy(self, trackerprop):
        with pytest.raises(NotImplementedError) as excinfo:
            copy.copy(trackerprop)
        assert "Shallow copy is not supported" in str(excinfo.value)

    def test_deep_copy(self, trackerprop):
        trackerprop.alpha.beta = 1
        deep_copy = copy.deepcopy(trackerprop)
        deep_copy.set_tracker(track_changes=True)
        deep_copy.z.t = 1
        assert [_ for _ in deep_copy.get_changed_history()] == ["/z/t"]


class TestDpath:
    """
    test dpath expression
    """

    def test_add_via_dnew(self, trackerprop):
        dnew(trackerprop, "/a/b/c", 1)
        assert [_ for _ in trackerprop.get_changed_history()] == ["/a/b/c"]

        trackerprop.clear_changed_history()
        assert [_ for _ in trackerprop.get_changed_history()] == []

        dnew(trackerprop, "/a/b/c", 1)
        assert [_ for _ in trackerprop.get_changed_history()] == ["/a/b/c"]

    def test_del_via_ddelete(self, trackerprop):
        """
        delete a key; clear changed history; and add again
        """
        dnew(trackerprop, "/a/b/c", 1)
        ddelete(trackerprop, "/a")
        assert [_ for _ in trackerprop.get_changed_history()] == []
        trackerprop.clear_changed_history()
        dnew(trackerprop, "/a/b/c", 1)
        assert [_ for _ in trackerprop.get_changed_history()] == ["/a/b/c"]

    def test_dset_ddelete(self, trackerprop):
        dnew(trackerprop, "/a1/b1/c1/d1", 1)
        dnew(trackerprop, "/a1/b2/c1/d1", 1)
        dnew(trackerprop, "/a1/b1/c2/d1", 1)
        dnew(trackerprop, "/a1/b1/c1/d2", 1)
        trackerprop.clear_changed_history()
        dset(trackerprop, "/a1/b1/c1/d1", 1)
        dset(trackerprop, "/a1/b2/c1/d1", 1)
        dset(trackerprop, "/a1/b1/c2/d1", 1)
        dset(trackerprop, "/a1/b1/c1/d2", 1)

        assert [_ for _ in trackerprop.get_changed_history()] == [
            "/a1/b1/c1/d1",
            "/a1/b1/c1/d2",
            "/a1/b1/c2/d1",
            "/a1/b2/c1/d1",
        ]

        ddelete(trackerprop, "/a1/b1/c1/d1")
        ddelete(trackerprop, "/a1/b2/c1/d1")
        ddelete(trackerprop, "/a1/b1/c2/d1")
        ddelete(trackerprop, "/a1/b1/c1/d2")

        assert [_ for _ in trackerprop.get_changed_history()] == []


class TestInitialization:
    def test_init_tuple(self):
        mydict = Dict((("a", 1), ("b", "2")))
        assert mydict == {"a": 1, "b": "2"}

    # TODO: test other initialization; mainly nested tuple;
    # some test cases covered in original repo
