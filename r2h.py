#!/usr/bin/env python3

"""
this is a (terrible) converter from word processor-like romaji to halfwidth katakana

- `-`: convert to chouonpu (only immediately after kana!)
- `^`: convert to chouonpu
- `z:`: convert to handakuten
- `z;`: convert to dakuten
- `z/`: convert to middle dot
- `.`: convert to ideographic full stop
- `,`: convert to ideographic comma
- `[`: convert to left corner bracket
- `]`: convert to right corner bracket

the rest is mostly a subset of the conversions described in https://github.com/yustier/jis-x-4063-2000

some of the differences from some other romaji input methods etc.:
1. no hiragana, since that does not exist in the halfwidth kana
2. no `wyi` and `wye`, since those do not exist in the halfwidth kana
3. no `xwa`, since that does not exist in the halfwidth kana
4. no `xke` and `xka`, since those do not exist in the halfwidth kana
5. `-` is only converted when it immediately follows kana, use `^` in other places
6. use `xaxa`/`lala`, `xyaxya`/`lyalya` etc. to repeat small `a`/`ya` etc.
7. no visual feedback during conversion
8. no kanji input, no other punctuation or special symbol input
9. instead of tchi etc. write cchi/tti etc.
10. instead of `mma`, `mbu`, `mpu` etc. write `nma`, `nbu`, `npu` etc.
11. instead of `dzu` write `du` for the voiced version of `tsu`/`tu`; `zu` is voiced `su`
12. instead of `tu`/`du` write `t'u`/`d'u` for `to`/`do` followed by small `u`
13. `xtu`, `xtsu`, `ltu`, or `ltsu` to get a small `tsu`/`tu`
14. `xa`, `xya`, etc. (or `la`, `lya`, etc.) to get small `a`, `ya`, etc.
15. repeat the first letter like `kka` to get small `tsu`/`tu` then `ka`, except `n` or vowels
16. write `nn` or `n'` (or `xn`) if `n` or a vowel follows it to get isolated/moraic `n`
17. write `ha`/`he`/`wo` for those particles, not `wa`/`e`/`o`
18. instead of `ti`/`di` write `t'i`/`d'i` for `te`/`de` followed by small `i`
19. there is no way to prevent conversion
20. instead of `tyu`/`dyu` write `t'yu`/`d'yu` for `te`/`de` followed by small `yu`
21. letter case is not meaningful or preserved
22. conversion failures may produce surprising garbage; behavior in unspecified cases may be surprising

"""

PUNCT_R = ".[],/^"
PUNCT_K = "｡｢｣､･ｰ"
MIDDOT_K = "･"
CHOUONPU_K = "ｰ"
WO_K = "ｦ"
X_K = "ｧｨｩｪｫ"
XYAIYUEYO_K = "ｬｨｭｪｮ"
XTU_K = "ｯ"
AUO_R = "auo"
AIUEO_R = "aiueo"
AIUEO_K = "ｱｲｳｴｵ"
I_K = "ｲ"
U_K = "ｳ"
XKSTNHMR_R = "xkstnhmr"
GZDB_R = "gzdb"
K_K = "ｶｷｸｹｺ"
C_K = "ｶｼｸｾｺ"
S_K = "ｻｼｽｾｿ"
T_K = "ﾀﾁﾂﾃﾄ"
TU_K = "ﾂ"
N_K = "ﾅﾆﾇﾈﾉ"
H_K = "ﾊﾋﾌﾍﾎ"
HU_K = "ﾌ"
M_K = "ﾏﾐﾑﾒﾓ"
YAIYUEYO_K = "ﾔｲﾕｴﾖ"
R_K = "ﾗﾘﾙﾚﾛ"
XKSTNHMR_K = [X_K, K_K, S_K, T_K, N_K, H_K, M_K, R_K]
KSTH_K = [K_K, S_K, T_K, H_K]
WA_K = "ﾜ"
NN_K = "ﾝ"
DAKUTEN_K = "ﾞ"
HANDAKUTEN_K = "ﾟ"

FLAG_KANA = "FLAG_KANA"


def r2k(*, ibuf, state, obuf, flags, getch):
    while True:
        # print(dict(ibuf=ibuf, state=state, obuf=obuf, flags=flags))
        if obuf:
            ch, obuf = obuf[:1], obuf[1:]
            # print(dict(ch=ch, obuf=obuf))
        else:
            if ibuf:
                ch, ibuf = ibuf[:1], ibuf[1:]
                # print(dict(ch=ch, ibuf=ibuf))
            else:
                ch = getch()
                # print(dict(ch=ch))
            aiueo_idx = AIUEO_R.find(ch.lower()) if ch else -1
            punct_idx = PUNCT_R.find(ch.lower()) if ch else -1
            if (state.lower() == "n") and (ch.lower() in ("n", "'")):
                ch, state = NN_K, ""
                flags = {FLAG_KANA}
            elif (state.lower() == "x") and ch.lower() == "n":
                ch, state = NN_K, ""
                flags = {FLAG_KANA}
            elif (
                ch
                and ch.lower() == state.lower()
                and (ch.lower() in XKSTNHMR_R + GZDB_R + "ywqcjfpvl")
            ):
                obuf = XTU_K
                continue
            elif (state.lower() in ("xy", "ly")) and (aiueo_idx >= 0):
                ch, state = XYAIYUEYO_K[aiueo_idx], ""
                flags = {FLAG_KANA}
                aiueo_idx = -1
            elif (state.lower() in ("x", "l")) and (aiueo_idx >= 0):
                ch, state = X_K[aiueo_idx], ""
                flags = {FLAG_KANA}
                aiueo_idx = -1
            elif (state.lower() in ("w", "p") and ch.lower() == "h") or (
                state.lower() in ("t", "d") and ch.lower() == "'"
            ):
                ch, state = "", state + ch
                continue
            elif state.lower() in ("t'", "d'") and ch.lower() == "u":
                ibuf = state[:1] + "ox" + ch + ibuf
                state = ""
                continue
            elif state.lower() in ("t'", "d'") and ch.lower() in ("i", "y"):
                ibuf = state[:1] + "ex" + ch + ibuf
                state = ""
                continue
            elif state.lower() == "wh" and aiueo_idx >= 0:
                state = ""
                if ch.lower() != "u":
                    ibuf = "x" + ch + ibuf
                ibuf = "u" + ibuf
                continue
            elif state.lower() == "ph" and aiueo_idx >= 0:
                state = ""
                ibuf = "pux" + ch + ibuf
                continue
            elif state and state.lower() in XKSTNHMR_R and (aiueo_idx >= 0):
                ch, state = XKSTNHMR_K[XKSTNHMR_R.index(state.lower())][aiueo_idx], ""
                flags = {FLAG_KANA}
                aiueo_idx = -1
            elif state.lower() == "c" and (aiueo_idx >= 0):
                ch, state = C_K[aiueo_idx], ""
                flags = {FLAG_KANA}
                aiueo_idx = -1
            elif state.lower() == "y" and (aiueo_idx >= 0):
                if ch.lower() == "e":
                    ibuf = "ix" + ch + ibuf
                    state = ""
                    continue
                ch, state = YAIYUEYO_K[aiueo_idx], ""
                flags = {FLAG_KANA}
                aiueo_idx = -1
            elif state.lower() == "w" and (aiueo_idx >= 0):
                if ch.lower() == "a":
                    ch = WA_K
                elif ch.lower() == "o":
                    ch = WO_K
                else:
                    if ch.lower() != "u":
                        ibuf = "x" + ch + ibuf
                    ch = U_K
                state = ""
                flags = {FLAG_KANA}
                aiueo_idx = -1
            elif state and state.lower() in GZDB_R and (aiueo_idx >= 0):
                ch, state = KSTH_K[GZDB_R.index(state.lower())][aiueo_idx], ""
                flags = {FLAG_KANA}
                aiueo_idx = -1
                ibuf = DAKUTEN_K + ibuf
            elif state.lower() == "p" and (aiueo_idx >= 0):
                ch, state = H_K[aiueo_idx], ""
                flags = {FLAG_KANA}
                aiueo_idx = -1
                ibuf = HANDAKUTEN_K + ibuf
            elif state.lower() == "c" and ch.lower() == "y":
                ibuf = "ty" + ibuf
                state = ""
                continue
            elif (
                state.lower() in ("k", "q", "g", "c", "s", "z", "h", "f")
                and ch.lower() == "w"
            ):
                ibuf = state + "ux" + ibuf
                state = ""
                continue
            elif state.lower() in ("t", "d") and ch.lower() == "w":
                ibuf = state + "ox" + ibuf
                state = ""
                continue
            elif state and state.lower() in "kstnhmrgzdbpj" and ch.lower() == "y":
                ibuf = state + "ixy" + ibuf
                state = ""
                continue
            elif state and state.lower() in "qfv" and ch.lower() == "y":
                ibuf = state + "uxy" + ibuf
                state = ""
                continue
            elif state.lower() == "n":
                ibuf = ch + ibuf
                ch, state = NN_K, ""
                flags = {FLAG_KANA}
            elif (
                ((state.lower() in ("x", "l")) and ch.lower() in ("y", "t"))
                or ((state.lower() in ("xt", "lt")) and ch.lower() == "s")
                or (state.lower() in ("c", "s", "t", "d") and ch.lower() == "h")
                or (state.lower() == "t" and ch.lower() == "s")
            ):
                ch, state = "", state + ch
                continue
            elif state.lower() == "sh" and aiueo_idx >= 0:
                state = ""
                if ch.lower() != "i":
                    ibuf = "xy" + ch + ibuf
                ibuf = "si" + ibuf
                continue
            elif state.lower() == "ts" and aiueo_idx >= 0:
                state = ""
                if ch.lower() != "u":
                    ibuf = "x" + ch + ibuf
                ibuf = "tu" + ibuf
                continue
            elif state.lower() in ("th", "dh") and aiueo_idx >= 0:
                ibuf = state[:1] + "exy" + ch + ibuf
                state = ""
                continue
            elif state.lower() == "ch" and aiueo_idx >= 0:
                state = ""
                if ch.lower() != "i":
                    ibuf = "xy" + ch + ibuf
                ibuf = "ti" + ibuf
                continue
            elif state.lower() == "q" and aiueo_idx >= 0:
                state = ""
                if ch.lower() != "u":
                    ibuf = "x" + ch + ibuf
                ibuf = "ku" + ibuf
                continue
            elif state.lower() == "j" and aiueo_idx >= 0:
                state = ""
                if ch.lower() != "i":
                    ibuf = "xy" + ch + ibuf
                ibuf = "zi" + ibuf
                continue
            elif state.lower() == "f" and aiueo_idx >= 0:
                state = ""
                if ch.lower() != "u":
                    ibuf = "x" + ch + ibuf
                ibuf = "hu" + ibuf
                continue
            elif state.lower() == "v" and aiueo_idx >= 0:
                state = ""
                if ch.lower() != "u":
                    ibuf = "x" + ch + ibuf
                ibuf = "uz;" + ibuf
                continue
            elif state.lower() in ("xt", "lt", "xts", "lts") and ch.lower() == "u":
                ch, state = XTU_K, ""
                flags = {FLAG_KANA}
                aiueo_idx = -1
            elif state.lower() == "z":
                if ch == ":":
                    ch, state = HANDAKUTEN_K, ""
                    flags = {FLAG_KANA}
                    iueo_idx, punct_idx = -1, -1
                elif ch == ";":
                    ch, state = DAKUTEN_K, ""
                    flags = {FLAG_KANA}
                elif ch == "/":
                    ch, state = MIDDOT_K, ""
                    flags = {FLAG_KANA}
            if state:
                obuf += state
                ibuf += ch
                state = ""
                flags = set()
                ch, obuf = obuf[:1], obuf[1:]
            else:
                assert state == ""
                if punct_idx >= 0:
                    ch = PUNCT_K[punct_idx]
                    flags = {FLAG_KANA}
                elif aiueo_idx >= 0:
                    ch = AIUEO_K[aiueo_idx]
                    flags = {FLAG_KANA}
                elif (ch == "-") and (FLAG_KANA in flags):
                    ch = CHOUONPU_K
                elif ch and (ch.lower() in XKSTNHMR_R + GZDB_R + "ywqcjfpvl"):
                    ch, state = "", ch
                    continue
                else:
                    flags = set()
        return ch, ibuf, state, obuf, flags


def r2ks(s):
    o = ""

    def getch():
        nonlocal s
        ch, s = s[:1], s[1:]
        return ch

    ibuf, state, obuf, flags = "", "", "", set()
    while True:
        ch, ibuf, state, obuf, flags = r2k(
            ibuf=ibuf, state=state, obuf=obuf, flags=flags, getch=getch
        )
        o += ch
        if ch + ibuf + state + obuf == "":
            break
        assert ch
    return o


def smoketest():
    assert r2ks("") == ""
    romaji_specimen = " ".join(
        """
  . [ ] , / wo xa xi xu xe xo xya xyu xyo xtu
  ^ a i u e o ka ki ku ke ko sa si su se so
  ta ti tu te to na ni nu ne no ha hi hu he ho ma
  mi mu me mo ya yu yo ra ri ru re ro wa nn z; z:
  """.split()
    )
    kana_specimen = " ".join(
        """
  ｡ ｢ ｣ ､ ･ ｦ ｧ ｨ ｩ ｪ ｫ ｬ ｭ ｮ ｯ
  ｰ ｱ ｲ ｳ ｴ ｵ ｶ ｷ ｸ ｹ ｺ ｻ ｼ ｽ ｾ ｿ
  ﾀ ﾁ ﾂ ﾃ ﾄ ﾅ ﾆ ﾇ ﾈ ﾉ ﾊ ﾋ ﾌ ﾍ ﾎ ﾏ
  ﾐ ﾑ ﾒ ﾓ ﾔ ﾕ ﾖ ﾗ ﾘ ﾙ ﾚ ﾛ ﾜ ﾝ ﾞ ﾟ
  """.split()
    )
    assert (
        r2ks(romaji_specimen) == kana_specimen
    ), f"r2ks({repr(romaji_specimen)}) failed, expected: \n {repr(kana_specimen)}, but got:\n {repr(r2ks(romaji_specimen))}"
    compact_romaji_specimen = ".[],/woxaxixuxexoxyaxyuxyoxtu^aiueokakikukekosasisusesotatitutetonaninunenohahihuhehomamimumemoyayuyorarirurerowannz;z:"
    compact_kana_specimen = (
        "｡｢｣､･ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝﾞﾟ"
    )
    assert (
        r2ks(compact_romaji_specimen) == compact_kana_specimen
    ), f"r2ks({repr(compact_romaji_specimen)}) failed, expected: \n {repr(compact_kana_specimen)}, but got:\n {repr(r2ks(compact_romaji_specimen))}"
    assert r2ks("-") == "-"
    assert r2ks("-123") == "-123"
    assert r2ks("123-456") == "123-456"
    assert r2ks("123-") == "123-"
    assert r2ks("z/") == "･"
    assert r2ks(".") == "｡"
    assert r2ks("[") == "｢"
    assert r2ks("]") == "｣"
    assert r2ks(",") == "､"
    assert r2ks("/") == "･"
    assert r2ks("^") == "ｰ"
    assert r2ks("a-") == "ｱｰ"
    assert r2ks("a^") == "ｱｰ"
    assert r2ks("a--") == "ｱｰｰ"
    assert r2ks("a^-") == "ｱｰｰ"
    assert r2ks("a-^") == "ｱｰｰ"
    assert r2ks("a---") == "ｱｰｰｰ"
    assert r2ks("a--^") == "ｱｰｰｰ"
    assert r2ks("a-^-") == "ｱｰｰｰ"
    assert r2ks("a-^^") == "ｱｰｰｰ"
    assert r2ks("a^--") == "ｱｰｰｰ"
    assert r2ks("a^-^") == "ｱｰｰｰ"
    assert r2ks("a^^-") == "ｱｰｰｰ"
    assert r2ks("a^^^") == "ｱｰｰｰ"
    assert r2ks("n'") == "ﾝ"
    for romaji, expected_kana in dict(
        aiueoyayuyo="ｱｲｳｴｵﾔﾕﾖ",
        _ye="ｲｪ",
        __yi="ｲ",
        kakikukekokyakyukyo="ｶｷｸｹｺｷｬｷｭｷｮ",
        _qaqiqeqo="ｸｧｸｨｸｪｸｫ",
        __qu="ｸ",
        __cacicuceco="ｶｼｸｾｺ",
        __kyikye="ｷｨｷｪ",
        sasisusesosyasyusyesyo="ｻｼｽｾｿｼｬｼｭｼｪｼｮ",
        __syi="ｼｨ",
        shashishushesho="ｼｬｼｼｭｼｪｼｮ",
        tatitutetotyatyutyetyo="ﾀﾁﾂﾃﾄﾁｬﾁｭﾁｪﾁｮ",
        chachichuchecho="ﾁｬﾁﾁｭﾁｪﾁｮ",
        _cyacyucyo="ﾁｬﾁｭﾁｮ",
        __cyicye="ﾁｨﾁｪ",
        naninunenonyanyunyo="ﾅﾆﾇﾈﾉﾆｬﾆｭﾆｮ",
        __nyinye="ﾆｨﾆｪ",
        hahihuhehohyahyuhyo="ﾊﾋﾌﾍﾎﾋｬﾋｭﾋｮ",
        __hyihye="ﾋｨﾋｪ",
        mamimumemomyamyumyo="ﾏﾐﾑﾒﾓﾐｬﾐｭﾐｮ",
        __myimye="ﾐｨﾐｪ",
        rarirureroryaryuryo="ﾗﾘﾙﾚﾛﾘｬﾘｭﾘｮ",
        __ryirye="ﾘｨﾘｪ",
        wawuwo="ﾜｳｦ",
        nn="ﾝ",
        n="ﾝ",
        n_="ﾝ",
        __xn="ﾝ",
        gagigugegogyagyugyo="ｶﾞｷﾞｸﾞｹﾞｺﾞｷﾞｬｷﾞｭｷﾞｮ",
        __gyigye="ｷﾞｨｷﾞｪ",
        zazizuzezozyazyuzyezyo="ｻﾞｼﾞｽﾞｾﾞｿﾞｼﾞｬｼﾞｭｼﾞｪｼﾞｮ",
        __zyi="ｼﾞｨ",
        jajijujejo="ｼﾞｬｼﾞｼﾞｭｼﾞｪｼﾞｮ",
        _jyajyujyo="ｼﾞｬｼﾞｭｼﾞｮ",
        __jyijye="ｼﾞｨｼﾞｪ",
        dadidudedodyadyudyedyo="ﾀﾞﾁﾞﾂﾞﾃﾞﾄﾞﾁﾞｬﾁﾞｭﾁﾞｪﾁﾞｮ",
        __dyi="ﾁﾞｨ",
        babibubebobyabyubyo="ﾊﾞﾋﾞﾌﾞﾍﾞﾎﾞﾋﾞｬﾋﾞｭﾋﾞｮ",
        __byibye="ﾋﾞｨﾋﾞｪ",
        papipupepopyapyupyo="ﾊﾟﾋﾟﾌﾟﾍﾟﾎﾟﾋﾟｬﾋﾟｭﾋﾟｮ",
        __pyipye="ﾋﾟｨﾋﾟｪ",
        xaxixuxexoxtu="ｧｨｩｪｫｯ",
        _xtsu="ｯ",
        __laliluleloltu="ｧｨｩｪｫｯ",
        __ltsu="ｯ",
        kkaggissuttennotennnou="ｯｶｯｷﾞｯｽｯﾃﾝｵﾃﾝﾉｳ",
        ggakkizzudde="ｯｶﾞｯｷｯｽﾞｯﾃﾞ",
        hhammirruwwo="ｯﾊｯﾐｯﾙｯｦ",
        bbappixxuxxyo="ｯﾊﾞｯﾋﾟｯｩｯｮ",
        xxxxtu="ｯｯｯｯ",
        xyaxyuxyo="ｬｭｮ",
        __xyi="ｨ",
        __lyalyilyulyelyo="ｬｨｭｪｮ",
        _wiwe="ｳｨｳｪ",
        _whiwhewho="ｳｨｳｪｳｫ",
        __whawhu="ｳｧｳ",
        _vavivuvevovyu="ｳﾞｧｳﾞｨｳﾞｳﾞｪｳﾞｫｳﾞｭ",
        __vyivyevyavyo="ｳﾞｨｳﾞｪｳﾞｬｳﾞｮ",
        _kwakwikwekwo="ｸｧｸｨｸｪｸｫ",
        __kwu="ｸｩ",
        ___cwacwicwucwecwo="ｸｧｸｨｸｩｸｪｸｫ",
        __qwaqwiqwuqweqwoqyaqyuqyo="ｸｧｸｨｸｩｸｪｸｫｸｬｸｭｸｮ",
        _gwa="ｸﾞｧ",
        __gwigwugwegwo="ｸﾞｨｸﾞｩｸﾞｪｸﾞｫ",
        __swaswiswusweswozwazwizwuzwezwo="ｽｧｽｨｽｩｽｪｽｫｽﾞｧｽﾞｨｽﾞｩｽﾞｪｽﾞｫ",
        tsatsutsetso="ﾂｧﾂﾂｪﾂｫ",
        _tsi="ﾂｨ",
        _twu="ﾄｩ",
        _t_u="ﾄｩ",
        __twatwitwetwo="ﾄｧﾄｨﾄｪﾄｫ",
        thi="ﾃｨ",
        _thu="ﾃｭ",
        _t_it_yu="ﾃｨﾃｭ",
        _dwu="ﾄﾞｩ",
        _d_u="ﾄﾞｩ",
        __dwadwidwedwo="ﾄﾞｧﾄﾞｨﾄﾞｪﾄﾞｫ",
        dhidhu="ﾃﾞｨﾃﾞｭ",
        _d_id_yu="ﾃﾞｨﾃﾞｭ",
        __dhadhedho="ﾃﾞｬﾃﾞｪﾃﾞｮ",
        fafifufefo="ﾌｧﾌｨﾌﾌｪﾌｫ",
        _fyu="ﾌｭ",
        __fyafyo="ﾌｬﾌｮ",
        _hwahwihwehwo="ﾌｧﾌｨﾌｪﾌｫ",
        __fwafwifwufwefwo="ﾌｧﾌｨﾌｩﾌｪﾌｫ",
        __phaphiphuphepho="ﾌﾟｧﾌﾟｨﾌﾟｩﾌﾟｪﾌﾟｫ",
    ).items():
        romaji = "'".join(romaji.lstrip("_").split("_"))
        assert (
            r2ks(romaji) == expected_kana
        ), f"r2ks({repr(romaji)}) failed, expected: \n {repr(expected_kana)}, but got:\n {repr(r2ks(romaji))}"
    long_romaji_specimen = """
     a  i  u  e  o  ya  yi  yu  ye  yo
    ka ki ku ke ko kya kyi kyu kye kyo
    sa si su se so sya syi syu sye syo
    ta ti tu te to tya tyi tyu tye tyo
    na ni nu ne no nya nyi nyu nye nyo
    ha hi hu he ho hya hyi hyu hye hyo
    ma mi mu me mo mya myi myu mye myo
    ra ri ru re ro rya ryi ryu rye ryo
    wa wi wu we wo

    ga gi gu ge go gya gyi gyu gye gyo
    za zi zu ze zo zya zyi zyu zye zyo
    da di du de do dya dyi dyu dye dyo
    ba bi bu be bo bya byi byu bye byo
    pa pi pu pe po pya pyi pyu pye pyo

     n       a-
    n'       ^
    nn       kka
    xn       xxa

      wha  whi  whu  whe  who
      kwa  kwi  kwu  kwe  kwo
       qa   qi   qu   qe   qo  qya       qyu       qyo
      qwa  qwi  qwu  qwe  qwo
      cwa  cwi  cwu  cwe  cwo
       ca   ci   cu   ce   co  cya  cyi  cyu  cye  cyo
      sha  shi  shu  she  sho
      swa  swi  swu  swe  swo
      cha  chi  chu  che  cho
      tsa  tsi  tsu  tse  tso
      tha  thi  thu  the  tho
      twa  twi  twu  twe  two
           t'i  t'u                     t'yu
       fa   fi   fu   fe   fo  fya       fyu       fyo
      hwa  hwi       hwe  hwo           hwyu
      fwa  fwi  fwu  fwe  fwo

       va   vi   vu   ve   vo  vya  vyi  vyu  vye  vyo
      gwa  gwi  gwu  gwe  gwo
       ja   ji   ju   je   jo  jya  jyi  jyu  jye  jyo
      zwa  zwi  zwu  zwe  zwo
      dha  dhi  dhu  dhe  dho
      dwa  dwi  dwu  dwe  dwo
           d'i  d'u                     d'yu
      pha  phi  phu  phe  pho

       xa   xi   xu   xe   xo  xya  xyi  xyu  xye  xyo
                xtu
               xtsu
       la   li   lu   le   lo  lya  lyi  lyu  lye  lyo
                ltu
               ltsu
    """
    long_kana_specimen = """
    ｱ   ｲ   ｳ   ｴ   ｵ   ﾔ   ｲ   ﾕ   ｲｪ  ﾖ
    ｶ   ｷ   ｸ   ｹ   ｺ   ｷｬ  ｷｨ  ｷｭ  ｷｪ  ｷｮ
    ｻ   ｼ   ｽ   ｾ   ｿ   ｼｬ  ｼｨ  ｼｭ  ｼｪ  ｼｮ
    ﾀ   ﾁ   ﾂ   ﾃ   ﾄ   ﾁｬ  ﾁｨ  ﾁｭ  ﾁｪ  ﾁｮ
    ﾅ   ﾆ   ﾇ   ﾈ   ﾉ   ﾆｬ  ﾆｨ  ﾆｭ  ﾆｪ  ﾆｮ
    ﾊ   ﾋ   ﾌ   ﾍ   ﾎ   ﾋｬ  ﾋｨ  ﾋｭ  ﾋｪ  ﾋｮ
    ﾏ   ﾐ   ﾑ   ﾒ   ﾓ   ﾐｬ  ﾐｨ  ﾐｭ  ﾐｪ  ﾐｮ
    ﾗ   ﾘ   ﾙ   ﾚ   ﾛ   ﾘｬ  ﾘｨ  ﾘｭ  ﾘｪ  ﾘｮ
    ﾜ   ｳｨ  ｳ   ｳｪ  ｦ

    ｶﾞ  ｷﾞ  ｸﾞ  ｹﾞ  ｺﾞ  ｷﾞｬ ｷﾞｨ ｷﾞｭ ｷﾞｪ ｷﾞｮ
    ｻﾞ  ｼﾞ  ｽﾞ  ｾﾞ  ｿﾞ  ｼﾞｬ ｼﾞｨ ｼﾞｭ ｼﾞｪ ｼﾞｮ
    ﾀﾞ  ﾁﾞ  ﾂﾞ  ﾃﾞ  ﾄﾞ  ﾁﾞｬ ﾁﾞｨ ﾁﾞｭ ﾁﾞｪ ﾁﾞｮ
    ﾊﾞ  ﾋﾞ  ﾌﾞ  ﾍﾞ  ﾎﾞ  ﾋﾞｬ ﾋﾞｨ ﾋﾞｭ ﾋﾞｪ ﾋﾞｮ
    ﾊﾟ  ﾋﾟ  ﾌﾟ  ﾍﾟ  ﾎﾟ  ﾋﾟｬ ﾋﾟｨ ﾋﾟｭ ﾋﾟｪ ﾋﾟｮ

      ﾝ      ｱｰ
      ﾝ      ｰ
      ﾝ      ｯｶ
      ﾝ      ｯｧ

    ｳｧ  ｳｨ  ｳ   ｳｪ  ｳｫ
    ｸｧ  ｸｨ  ｸｩ  ｸｪ  ｸｫ
    ｸｧ  ｸｨ  ｸ   ｸｪ  ｸｫ  ｸｬ      ｸｭ      ｸｮ
    ｸｧ  ｸｨ  ｸｩ  ｸｪ  ｸｫ
    ｸｧ  ｸｨ  ｸｩ  ｸｪ  ｸｫ
    ｶ   ｼ   ｸ   ｾ   ｺ   ﾁｬ  ﾁｨ  ﾁｭ  ﾁｪ  ﾁｮ
    ｼｬ  ｼ   ｼｭ  ｼｪ  ｼｮ
    ｽｧ  ｽｨ  ｽｩ  ｽｪ  ｽｫ
    ﾁｬ  ﾁ   ﾁｭ  ﾁｪ  ﾁｮ
    ﾂｧ  ﾂｨ  ﾂ   ﾂｪ  ﾂｫ
    ﾃｬ  ﾃｨ  ﾃｭ  ﾃｪ  ﾃｮ
    ﾄｧ  ﾄｨ  ﾄｩ  ﾄｪ  ﾄｫ
        ﾃｨ  ﾄｩ                  ﾃｭ
    ﾌｧ  ﾌｨ  ﾌ   ﾌｪ  ﾌｫ  ﾌｬ      ﾌｭ      ﾌｮ
    ﾌｧ  ﾌｨ      ﾌｪ  ﾌｫ          ﾌｭ
    ﾌｧ  ﾌｨ  ﾌｩ  ﾌｪ  ﾌｫ

    ｳﾞｧ ｳﾞｨ ｳﾞ  ｳﾞｪ ｳﾞｫ ｳﾞｬ ｳﾞｨ ｳﾞｭ ｳﾞｪ ｳﾞｮ
    ｸﾞｧ ｸﾞｨ ｸﾞｩ ｸﾞｪ ｸﾞｫ
    ｼﾞｬ  ｼﾞ ｼﾞｭ ｼﾞｪ ｼﾞｮ ｼﾞｬ ｼﾞｨ ｼﾞｭ ｼﾞｪ ｼﾞｮ
    ｽﾞｧ ｽﾞｨ ｽﾞｩ ｽﾞｪ ｽﾞｫ
    ﾃﾞｬ ﾃﾞｨ ﾃﾞｭ ﾃﾞｪ ﾃﾞｮ
    ﾄﾞｧ ﾄﾞｨ ﾄﾞｩ ﾄﾞｪ ﾄﾞｫ
        ﾃﾞｨ ﾄﾞｩ                 ﾃﾞｭ
    ﾌﾟｧ ﾌﾟｨ ﾌﾟｩ ﾌﾟｪ ﾌﾟｫ

    ｧ   ｨ   ｩ   ｪ   ｫ   ｬ  ｨ  ｭ  ｪ  ｮ
            ｯ
            ｯ
    ｧ   ｨ   ｩ   ｪ   ｫ   ｬ  ｨ  ｭ  ｪ  ｮ
            ｯ
            ｯ
    """
    assert (
        r2ks(long_romaji_specimen).split() == long_kana_specimen.split()
    ), f"r2ks({repr(long_romaji_specimen)}) failed, expected: \n {repr(long_kana_specimen)}, but got:\n {repr(r2ks(long_romaji_specimen))}"
    assert r2ks("Ra-men") == "ﾗ-ﾒﾝ"
    assert r2ks("cyocore-to") == "ﾁｮｺﾚ-ﾄ"
    assert r2ks("chokore-to") == "ﾁｮｺﾚ-ﾄ"
    assert r2ks("tyokore-to") == "ﾁｮｺﾚ-ﾄ"
    assert r2ks("tixyokore-to") == "ﾁｮｺﾚ-ﾄ"
    assert r2ks("chilyokore-to") == "ﾁｮｺﾚ-ﾄ"
    assert r2ks("KYANTO/BAI/MI-/RABU") == "ｷｬﾝﾄ･ﾊﾞｲ･ﾐ-･ﾗﾌﾞ"
    assert r2ks("byu-t'ifuru/sande-") == "ﾋﾞｭ-ﾃｨﾌﾙ･ｻﾝﾃﾞ-"
    assert r2ks("BarakuZ/Obama") == "ﾊﾞﾗｸ･ｵﾊﾞﾏ"
    assert r2ks("Pa-sonaru/Conpyu-ta-") == "ﾊﾟ-ｿﾅﾙ･ｺﾝﾋﾟｭ-ﾀ-"
    assert r2ks("Da/Vinchi=DaVinchi") == "ﾀﾞ･ｳﾞｨﾝﾁ=ﾀﾞｳﾞｨﾝﾁ"
    assert r2ks("VARISU") == "ｳﾞｧﾘｽ"
    assert r2ks("I-SU") == "ｲｰｽ"
    assert r2ks("I^su") == "ｲｰｽ"


smoketest()

import sys
import unicodedata


def main():
    """
    When invoked with no arguments, this acts as a filter from stdin to stdout.
    When invoked with arguments, each is treated as a filename and filtered to stdout.
    The special filename `-` refers to stdin.
    """
    ibuf, state, obuf, flags = "", "", "", set()
    _, *filenames = sys.argv
    filenames = filenames or ["-"]
    for filename in filenames:
        with sys.stdin if filename == "-" else open(filename, "r") as source:
            while True:
                ch, ibuf, state, obuf, flags = r2k(
                    ibuf=ibuf,
                    state=state,
                    obuf=obuf,
                    flags=flags,
                    getch=lambda: source.read(1),
                )
                if ch + ibuf + state + obuf == "":
                    break
                assert ch
                if False:
                    print(
                        dict(
                            ch=ch,
                            ch_name=unicodedata.name(ch, f"U+{ord(ch):04X}"),
                            ibuf=ibuf,
                            state=state,
                            obuf=obuf,
                            flags=flags,
                        )
                    )
                print(ch, end="", flush=True)


if __name__ == "__main__":
    main()
