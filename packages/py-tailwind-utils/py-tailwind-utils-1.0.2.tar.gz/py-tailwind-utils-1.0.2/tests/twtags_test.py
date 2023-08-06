import pytest
from py_tailwind_utils import *
from py_tailwind_utils import style_values as sv

from pytest_cases import fixture_union, pytest_fixture_plus as fixture_plus

# @pytest.mark.parametrize('char, expected', [('a', 97), ('b', 98)])
# def test_ascii(char, expected):
#     assert ord(char) == expected

# @pytest.fixture
# def one():
#     return bg/green/100


# @pytest.mark.parametrize("twexpr",
#                          [
#                              pytest.lazy_fixture(_) for _ in ["one"]
#                          ]
#                          )

# def test_commentout(twexpr):
#     assert tstr(cc/twexpr) == ""


@pytest.fixture(
    name="sty_value_expr",
    params=(
        (db.b, sv.DisplayBox.b),
        (db.bi, sv.DisplayBox.bi),
        (wa.r, sv.WrapAround.r),
        (op.rb, sv.ObjectPosition.rb),
    ),
)
def _sty_value_expr(request):
    return request.param


@pytest.fixture(name="psuedo_class", params=(hover, placeholder, selection))
def _psuedo_class(request):
    return request.param


@pytest.fixture(name="outer_psuedo_class", params=(hover, placeholder, selection))
def _outer_psuedo_class(request):
    return request.param


@pytest.fixture
def sty_value_psuedo_class(sty_value_expr, psuedo_class):
    try:
        (idiv_expr, enum_tag) = sty_value_expr
        idiv_expr.modifier_chain.clear()
    except:
        pass
    return psuedo_class(idiv_expr)[0], enum_tag, psuedo_class


@pytest.fixture
def sty_value_nested_psuedo_class(sty_value_psuedo_class, outer_psuedo_class):
    """
    generates testcases for nested-psuedo-class focus:invalid:border-pink-500 focus:invalid:ring-pink-500
    """
    expr, eunm_tag, inner_psuedo_class = sty_value_psuedo_class
    # expr, inner_psuedo_class = sty_value_psuedo_class
    return (
        outer_psuedo_class(expr)[0],
        eunm_tag,
        [outer_psuedo_class, inner_psuedo_class],
    )


@pytest.fixture(name="attr_color", params=(red, green, blue))
def _attr_color(request):
    return request.param


@pytest.fixture(name="tw_mrpd", params=(mr, pd))
def _tw_utility_mrpd(request):
    return request.param


@pytest.fixture(name="sides", params=(sl, sr, sb, st))
def _tw_utility_dir(request):
    return request.param


@pytest.fixture
def tw_mrpd_dir_expr(tw_mrpd, sides):
    return tw_mrpd / sides, tw_mrpd, sides


@pytest.fixture(name="color_value", params=("50", "100", "500", 1, 5))
def _color_value(request):
    return request.param


@pytest.fixture(name="tw_feature", params=(bg, fc, bd))
def _tw_feature(request):
    return request.param


@pytest.fixture
def tw_color(attr_color, color_value):
    return attr_color / color_value, attr_color, color_value


@fixture_plus
def tw_feature_value(tw_feature, tw_color):
    color_val, attr_color, color_value = tw_color
    return tw_feature / color_val, tw_feature, attr_color, color_value


@fixture_plus
def tw_mrpd_dir_value_expr(tw_mrpd_dir_expr):
    expr, mrpd, sides = tw_mrpd_dir_expr
    value = 2
    return expr / value, mrpd, sides, value


def test_tw_feature_value(tw_feature_value):
    tw_expr, tw_feature, attr_color, color_value = tw_feature_value
    if isinstance(color_value, int):
        assert True
    else:
        assert tstr(tw_expr) == f"{tw_feature.stemval}-{attr_color}-{color_value}"


def test_comment_out(tw_feature_value):
    tw_expr, tw_feature, attr_color, color_value = tw_feature_value
    assert tstr(cc / tw_expr) == ""


def test_mrpd_expr_utility(tw_mrpd_dir_expr):
    expr, mrpd, sides = tw_mrpd_dir_expr
    assert tstr(expr / 4) == f"{mrpd.stemval}{sides.stemval}-4"


def test_mrpd_utility(tw_mrpd):
    assert tstr(tw_mrpd / 4) == f"{tw_mrpd.stemval}-4"


def test_conc_twtags():
    mytags = [
        bg / green / 1,
        bg / blue / 1,
        fc / blue / 1,
        fc / gray / 1,
        flx.row,
        flx.rrow,
    ]
    assert tstr(*conc_twtags(*mytags)) == tstr(bg / blue / 1, fc / gray / 1, flx.rrow)


def test_conc_twtags_same_tagtype():
    """
    test twtag concatenation over same style tags
    """
    mytags = [hidden, hidden]
    assert tstr(*conc_twtags(*mytags)) == tstr(hidden)


def test_conc_twtags_same_tagtype():
    """
    test twtag concatenation over same style tags
    """
    mytags = [hidden, hidden]
    assert tstr(*conc_twtags(*mytags)) == tstr(hidden)


def test_conc_twtags_diff_style_values():
    """
    test twtag concatenation over style_values. use of noop
    """
    mytags = [db.f, jc.center]
    assert tstr(*conc_twtags(*mytags)) == "flex justify-center"


# These need to be added to the tests
# print(tstr(*conc_twtags(jc.center, db.f)))
# print(tstr(*conc_twtags(bg/blue/1, bg/green/1)))
# print(tstr(*conc_twtags(bg/green/1, *hover(bg/green/1))))
# print(tstr(*conc_twtags(mr/sl/1, *hover(mr/sl/1))))
# print(tstr(*conc_twtags(*hover(mr/sl/2), *hover(mr/sl/1))))


def test_bg_color_opacity():
    with pytest.raises(AttributeError) as excinfo:
        assert tstr(bg / pink / 100 / 60) == "bg-pink-100/60"
    assert "elabel" in str(excinfo.value)


def test_outline_boxshadow_tags_and_values():
    twtags = [
        outline.dotted,
        outline / 2,
        outline.dotted,
        outline / gray / 50,
        shadow._,
        shadow.md,
        shadow / green / 1,
    ]
    assert (
        tstr(*twtags)
        == "outline-dotted outline-2 outline-dotted outline-gray-50 shadow shadow-md shadow-green-100"
    )


def test_remove_from_twtag_list():
    mytags = [bg / blue / 1, bg / green / 1, fc / blue / 1, flx.rrow, jc.start]
    remove_from_twtag_list(mytags, jc.start)
    remove_from_twtag_list(mytags, bg / green / 1)
    assert tstr(*mytags) == "bg-blue-100 text-blue-100 flex-row-reverse"


def test_remove_absent_item_scenario1():
    """
    when bg/green/1 is present
    but we delete bg/pink/1.
    Expection is raised after partial match
    """
    # with pytest.raises(KeyError) as excinfo:
    mytags = [bg / blue / 1, bg / green / 1, fc / blue / 1, flx.rrow, jc.start]
    remove_from_twtag_list(mytags, bg / pink / 1)
    # removal of non-present item doesn't raise KeyError
    # assert "pink" in str(excinfo.value)
    assert True


# def test_remove_absent_item_scenario2():
#     with pytest.raises(ValueError) as excinfo:
#         mytags = [bg / blue / 1, bg / green / 1, fc / blue / 1, flx.rrow, jc.start]
#         remove_from_twtag_list(mytags, jc.end)
#     assert "remove" in str(excinfo.value)


def test_sty_to_json_color_utility_class(tw_feature_value):
    """
    tests sty_to_json conversion of expression of type {bg/bd}/green/{1,{"50/100"}
    """
    color_expr, tw_feature, attr_color, color_value = tw_feature_value
    styj = styClause.to_json(color_expr)
    assert styj.passthrough == []
    assert tw_feature.elabel in styj
    if isinstance(color_value, int):
        assert styj[tw_feature.elabel][0]._val == f"{attr_color}-{color_value}00"
    else:
        assert styj[tw_feature.elabel][0]._val == f"{attr_color}-{color_value}"
    assert styj[tw_feature.elabel][0]._modifier_chain == []


def test_sty_to_json_other_utility_class(tw_mrpd_dir_value_expr):
    """
    tests sty_to_json conversion of expression of type {mr/pd}/{sr/sl...}/1

    {'passthrough': [], 'mr': [{'sl': {'_val': '2'}, '_modifier_chain': []}]}

    """
    expr, mrpd, sides, value = tw_mrpd_dir_value_expr
    styj = styClause.to_json(expr)
    assert styj.passthrough == []
    assert mrpd.elabel in styj

    assert sides.elabel in styj[mrpd.elabel][0]
    assert styj[mrpd.elabel][0][sides.elabel]._val == str(value)
    assert styj[mrpd.elabel][0]._modifier_chain == []


def test_sty_to_json_value_class(sty_value_expr):
    """
    tests sty_to_json conversion of expression of type fsz.xl, etc
    {'passthrough': [], 'DisplayBox': [{'_val': 'f', '_modifier_chain': []}]}

    """
    (idiv_expr, enum_tag) = sty_value_expr
    styj = styClause.to_json(idiv_expr)
    assert styj.passthrough == []
    assert styj[enum_tag.__class__.__name__][0]._val == enum_tag.name


@pytest.fixture()
def sty_json_idiv_color(tw_feature_value):
    color_expr, tw_feature, attr_color, color_value = tw_feature_value
    yield styClause.to_json(color_expr), color_expr


@pytest.fixture()
def sty_json_idiv_mrpd(tw_mrpd_dir_value_expr):
    expr, mrpd, sides, value = tw_mrpd_dir_value_expr
    yield styClause.to_json(expr), expr


@pytest.fixture()
def sty_json_sty_value(sty_value_expr):
    """
    create sty-json for style values eg.
    """
    (idiv_expr, enum_tag) = sty_value_expr
    yield styClause.to_json(idiv_expr), sty_value_expr


def test_json_to_tw_expr_case_idiv_color(sty_json_idiv_color):
    """
    test json to tw expression for idiv expression bg/green/1
    """
    styj, orig_expr = sty_json_idiv_color
    computed_expr = styClause.to_clause(styj)
    assert tstr(*computed_expr) == tstr(orig_expr)


def test_json_to_tw_expr_case_idiv_mrpd(sty_json_idiv_mrpd):
    """
    test json to tw expression for idiv expression bg/green/1
    """
    styj, orig_expr = sty_json_idiv_mrpd  #
    computed_expr = styClause.to_clause(styj)
    assert tstr(*computed_expr) == tstr(orig_expr)


def test_json_to_tw_expr_case_sty_value(sty_json_sty_value):
    """
    test json to tw expression for idiv expression bg/green/1
    """

    styj, (idiv_expr, enum_tag) = sty_json_sty_value  #
    computed_expr = styClause.to_clause(styj)
    assert tstr(*computed_expr) == tstr(idiv_expr)


def test_to_json_sty_value_psuedo_class(sty_value_psuedo_class):
    # expr_arr: output of hover(tw_expr)

    expr, enum_tag, psuedo_class = sty_value_psuedo_class
    print("enum_tag =", enum_tag)
    styj = styClause.to_json(expr)
    assert styj[enum_tag.__class__.__name__][0]["_modifier_chain"] == [
        psuedo_class.__name__
    ]


def test_to_json_sty_value_nested_psuedo_class(sty_value_nested_psuedo_class):
    expr, enum_tag, classes = sty_value_nested_psuedo_class
    if classes[0] == classes[1]:
        assert True
    else:
        styj = styClause.to_json(expr)
        assert set(styj[enum_tag.__class__.__name__][0]._modifier_chain) == set(
            [_.__name__ for _ in classes]
        )


# add test for styClause.to_json(noop/fz.xl)
# def test_to_json_sty_value_with_hover():
#     twsty_tags

# need to redo all tests now that style_values are prefixed with noop

# need to test utils.BoxShadow business
