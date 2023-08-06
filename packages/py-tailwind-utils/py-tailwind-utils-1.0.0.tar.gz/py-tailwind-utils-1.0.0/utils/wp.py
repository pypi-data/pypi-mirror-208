import justpy as jp
import ofjustpy as oj
import ofjustpy_react as ojr
from aenum import Enum
from tailwind_tags import style_values as sv
from tailwind_tags import style_tags as st
import tailwind_tags as twt

# ========== mapping from tw names to short descriptor names =========
map_twname= {
    "DisplayBox":"db",
"WrapAround":"wa",
"ClearWrap":"wc",
"ObjectFit":"of",
"ObjectPosition":"op",
"Visibility":"visibility",
"FlexLayout":"flx",
"JustifyContent":"jc",
"JustifyItems":"ji",
"JustifySelf":"js",
"AlignContent":"ac",
"AlignItems":"ai",
"PlaceContent":"pc",
"PlaceItems":"pi",
"PlaceSelf":"ps",
"FontFamily":"ff",
"FontSize":"fz",
"FontWeight":"fw",
"LetterSpace":"ls",
"LineHeight":"lh",
"ListItems":"li",
"TextAlign":"ta",
"VerticalAlign":"va",
"BackgroundAttachment":"ba",
"BorderRadius":"bdr",
"BorderStyle":"bds",
"BoxShadow":"bsw",
"Table":"tbl",
"Outline":"outline",
"BoxTopo":"bt",
"PlacementPosition":"ppos",
"BoxSizing":"boxsz",
"Prose":"prse",
"GridFlow":"gf",
"GridAuto":"ga",
}

def build_components(session_manager):
    with session_manager.uictx("twreference") as _twreferencectx:
        _ictx = _twreferencectx
        def handle_twSty_select(dbref, msg):
            ecls = sv.styValueDict[dbref.stub.key]  # enum class
            selected_attr = getattr(ecls, dbref.value)
            print("handle_twSty_select: ", ecls, " ", selected_attr)
            return _ictx.styValuesPanel.target.stub.spath, selected_attr


        def hc_enum_selector(attrClass: Enum):
            """Build selector htmlcomponent for enum class
            attrClass: enum type that describes a tailwind utility -- e.g. fw, fsz, etc.
            """
            #pcp = [shdw.md, bg/gray/1]
            name = attrClass.__name__
            return oj.WithBanner_(f"{name}Banner", f"{name} ({map_twname[name]})", oj.Select_(name, [oj.Option_(_.name, text = _.value , value=_.name) for _ in attrClass]).event_handle(oj.change, handle_twSty_select))
        #do not mix uictx and lambda
        cgens = [_ for _ in map(lambda kv: hc_enum_selector(kv[1]), sv.styValueDict.items())]
        oj.Subsection_("styValuesPanel", "Tailwing Style Directives",
                       oj.StackG_("content", num_cols=4,  cgens=cgens)
                       )

        # ================= panel to list style tags =================
        def hc_twtag_info(tagC):
            """
            tagC: tailwind tag class defined in style_tags
            """
            return oj.StackW_(tagC.__class__.__name__[1:], cgens=[oj.Span_("description", text=tagC.taghelp+":", pcp=[twt.bg/twt.slate/1]), oj.Span_("Notation", text=tagC.elabel, pcp=[twt.fw.bold])])
        cgens = map(lambda kv: hc_twtag_info(kv[1]), st.styTagDict.items())
        tagcontent_ = oj.StackG_("content", cgens=cgens, num_cols=5)
        panel_ = oj.Subsection_(
            "tagRefPanel", "Tailwind style tags", tagcontent_)
    return panel_

    
def wp_twtags_ref(request):
    session_id = request.session_id
    session_manager = oj.get_session_manager(session_id)
    stubStore = session_manager.stubStore
    with oj.sessionctx(session_manager):
        build_components(session_manager)
        oj.Container_("tlc",
                          cgens = [stubStore.twreference.styValuesPanel,
                                   oj.Divider_("sep", pcp=[twt.mr/twt.st/8, twt.mr/twt.sb/8]),
                                   stubStore.twreference.tagRefPanel
                                   ],
                          pcp=[twt.H/"screen", twt.bg/twt.gray/"100/20"])
        wp = oj.WebPage_("Reference to tw tags and values",
                         cgens= [stubStore.tlc],
                         template_file='svelte.html',
                             title="Tailwind constructs reference page")()

        return wp

app = jp.app
jp.justpy(wp_twtags_ref, start_server=False)
    
