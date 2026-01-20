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
- `z-`: convert to hyphen-minus

ASCII backspace (Ctrl-H, 0x08) and Delete/Rubout (Ctrl-?, 0x7F) can erase parts of in-progress conversions, but it won't work in a fully intuitive way since the original input characters are not preserved. When no conversion is in progress, they will back up the is-it-kana state used to determine `-` behavior, but this only remembers the most recent 8 characters. Any other ASCII control character will cause the kana state history to be cleared, though.

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
16. write `nn` or `n'` (or `xn`/`ln`) if `n` or a vowel follows it to get isolated/moraic `n`
17. write `ha`/`he`/`wo` for those particles, not `wa`/`e`/`o`
18. instead of `ti`/`di` write `t'i`/`d'i` for `te`/`de` followed by small `i`
19. there is no way to prevent conversion
20. instead of `tyu`/`dyu` write `t'yu`/`d'yu` for `te`/`de` followed by small `yu`
21. letter case is not meaningful or preserved
22. conversion failures may produce surprising garbage; behavior in unspecified cases may be surprising

"""

BACKSPACE_A = "\b"
RUBOUT_A = "\x7f"
PUNCT_A = ".[],/"
PUNCT_K = "｡｢｣､･"
MIDDOT_A = PUNCT_A[4]
MIDDOT_K = PUNCT_K[4]
CHOUONPU_A = "^"
CHOUONPU_K = "ｰ"
HYPHEN_MINUS_A = "-"
WO_K = "ｦ"
X_R = "x"
L_R = "l"
X_K = "ｧｨｩｪｫ"
XYAYUYO_K = "ｬｭｮ"
XYAIYUEYO_K = XYAYUYO_K[0] + X_K[1] + XYAYUYO_K[1] + X_K[3] + XYAYUYO_K[2]
XTU_K = "ｯ"
AIUEO_R = "aiueo"
AIUEO_K = "ｱｲｳｴｵ"
A_R = AIUEO_R[0]
I_R = AIUEO_R[1]
U_R = AIUEO_R[2]
U_K = AIUEO_K[2]
E_R = AIUEO_R[3]
O_R = AIUEO_R[4]
KSTNHMR_R = "kstnhmr"
K_R = KSTNHMR_R[0]
K_K = "ｶｷｸｹｺ"
S_R = KSTNHMR_R[1]
S_K = "ｻｼｽｾｿ"
C_R = "c"
C_K = K_K[0] + S_K[1] + K_K[2] + S_K[3] + K_K[4]
T_R = KSTNHMR_R[2]
T_K = "ﾀﾁﾂﾃﾄ"
TU_K = T_K[2]
N_R = KSTNHMR_R[3]
N_K = "ﾅﾆﾇﾈﾉ"
H_R = KSTNHMR_R[4]
H_K = "ﾊﾋﾌﾍﾎ"
HU_K = H_K[2]
M_K = "ﾏﾐﾑﾒﾓ"
Y_R = "y"
YAYUYO_K = "ﾔﾕﾖ"
R_K = "ﾗﾘﾙﾚﾛ"
YAIYUEYO_K = YAYUYO_K[0] + AIUEO_K[1] + YAYUYO_K[1] + AIUEO_K[3] + YAYUYO_K[2]
XLKSTNHMR_R = X_R + L_R + KSTNHMR_R
XLKSTNHMR_K = [X_K, X_K, K_K, S_K, T_K, N_K, H_K, M_K, R_K]
GZDB_R = "gzdb"
G_R = GZDB_R[0]
Z_R = GZDB_R[1]
D_R = GZDB_R[2]
KSTH_K = [K_K, S_K, T_K, H_K]
WA_K = "ﾜ"
W_R = "w"
NN_K = "ﾝ"
DAKUTEN_K = "ﾞ"
DAKUTEN_R = Z_R + ";"
HANDAKUTEN_K = "ﾟ"
HANDAKUTEN_R = Z_R + ":"
V_R = "v"
Q_R = "q"
J_R = "j"
F_R = "f"
P_R = "p"
YWQCJFPV_R = Y_R + W_R + Q_R + C_R + J_R + F_R + P_R + V_R
LEAD_R = XLKSTNHMR_R + GZDB_R + YWQCJFPV_R
KSTNHMRGZDBPJ_R = KSTNHMR_R + GZDB_R + P_R + J_R
APOSTROPHE_A = "'"

ALL_R = AIUEO_R + XLKSTNHMR_R + GZDB_R + YWQCJFPV_R
assert sorted(ALL_R) == [chr(cc) for cc in range(ord("a"), 1 + ord("z"))]

ALL_K = (
    PUNCT_K
    + WO_K
    + X_K
    + XYAYUYO_K
    + XTU_K
    + CHOUONPU_K
    + AIUEO_K
    + K_K
    + S_K
    + T_K
    + N_K
    + H_K
    + M_K
    + YAYUYO_K
    + R_K
    + WA_K
    + NN_K
    + DAKUTEN_K
    + HANDAKUTEN_K
)
assert ALL_K == bytes(range(0xA1, 0xE0)).decode("cp932")

EMPTY_STATE = ""


def r2k(*, ibuf, state, obuf, flags, getch):
    while True:
        if obuf:
            ch, obuf = obuf[:1], obuf[1:]
        else:
            if ibuf:
                ch, ibuf = ibuf[:1], ibuf[1:]
            else:
                ch = getch()
            if ch in (BACKSPACE_A, RUBOUT_A):
                if state:
                    state = state[:-1]
                    continue
                else:
                    flags = (flags & 0x7F) << 1
                    return ch, ibuf, state, obuf, flags
            aiueo_idx = AIUEO_R.find(ch.lower()) if ch else -1
            punct_idx = PUNCT_A.find(ch.lower()) if ch else -1
            if (state.lower() == N_R) and (ch.lower() in (N_R, APOSTROPHE_A)):
                ch, state = NN_K, EMPTY_STATE
            elif state.lower() in (X_R, L_R) and ch.lower() == N_R:
                ch, state = NN_K, EMPTY_STATE
            elif ch and ch.lower() == state.lower() and (ch.lower() in LEAD_R):
                obuf = XTU_K
                continue
            elif (state.lower() in (X_R + Y_R, L_R + Y_R)) and (aiueo_idx >= 0):
                ch, state = XYAIYUEYO_K[aiueo_idx], EMPTY_STATE
                aiueo_idx = -1
            elif (state.lower() in (X_R, L_R)) and (aiueo_idx >= 0):
                ch, state = X_K[aiueo_idx], EMPTY_STATE
                aiueo_idx = -1
            elif (state.lower() in (W_R, P_R) and ch.lower() == H_R) or (
                state.lower() in (T_R, D_R) and ch.lower() == APOSTROPHE_A
            ):
                state += ch
                continue
            elif (
                state.lower() in (T_R + APOSTROPHE_A, D_R + APOSTROPHE_A)
                and ch.lower() == U_R
            ):
                ibuf = state[:1] + O_R + X_R + ch + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() in (
                T_R + APOSTROPHE_A,
                D_R + APOSTROPHE_A,
            ) and ch.lower() in (I_R, Y_R):
                ibuf = state[:1] + E_R + X_R + ch + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() == W_R + H_R and aiueo_idx >= 0:
                if ch.lower() != U_R:
                    ibuf = X_R + ch + ibuf
                ibuf = U_R + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() == P_R + H_R and aiueo_idx >= 0:
                ibuf = state[:1] + U_R + X_R + ch + ibuf
                state = EMPTY_STATE
                continue
            elif state and state.lower() in XLKSTNHMR_R and (aiueo_idx >= 0):
                ch, state = (
                    XLKSTNHMR_K[XLKSTNHMR_R.index(state.lower())][aiueo_idx],
                    EMPTY_STATE,
                )
                aiueo_idx = -1
            elif state.lower() == C_R and (aiueo_idx >= 0):
                ch, state = C_K[aiueo_idx], EMPTY_STATE
                aiueo_idx = -1
            elif state.lower() == Y_R and (aiueo_idx >= 0):
                if ch.lower() == E_R:
                    ibuf = I_R + X_R + ch + ibuf
                    state = EMPTY_STATE
                    continue
                ch, state = YAIYUEYO_K[aiueo_idx], EMPTY_STATE
                aiueo_idx = -1
            elif state.lower() == W_R and (aiueo_idx >= 0):
                if ch.lower() == A_R:
                    ch = WA_K
                elif ch.lower() == O_R:
                    ch = WO_K
                else:
                    if ch.lower() != U_R:
                        ibuf = X_R + ch + ibuf
                    ch = U_K
                state = EMPTY_STATE
                aiueo_idx = -1
            elif state and state.lower() in GZDB_R and (aiueo_idx >= 0):
                ch, state = KSTH_K[GZDB_R.index(state.lower())][aiueo_idx], EMPTY_STATE
                aiueo_idx = -1
                ibuf = DAKUTEN_K + ibuf
            elif state.lower() == P_R and (aiueo_idx >= 0):
                ch, state = H_K[aiueo_idx], EMPTY_STATE
                aiueo_idx = -1
                ibuf = HANDAKUTEN_K + ibuf
            elif state.lower() == C_R and ch.lower() == Y_R:
                ibuf = T_R + Y_R + ibuf
                state = EMPTY_STATE
                continue
            elif (
                state.lower() in (K_R, Q_R, G_R, C_R, S_R, Z_R, H_R, F_R)
                and ch.lower() == W_R
            ):
                ibuf = state + U_R + X_R + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() in (T_R, D_R) and ch.lower() == W_R:
                ibuf = state + O_R + X_R + ibuf
                state = EMPTY_STATE
                continue
            elif state and state.lower() in KSTNHMRGZDBPJ_R and ch.lower() == Y_R:
                ibuf = state + I_R + X_R + Y_R + ibuf
                state = EMPTY_STATE
                continue
            elif state and state.lower() in Q_R + F_R + V_R and ch.lower() == Y_R:
                ibuf = state + U_R + X_R + Y_R + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() == N_R:
                ibuf = ch + ibuf
                ch, state = NN_K, EMPTY_STATE
            elif (
                ((state.lower() in (X_R, L_R)) and ch.lower() in (Y_R, T_R))
                or ((state.lower() in (X_R + T_R, L_R + T_R)) and ch.lower() == S_R)
                or (state.lower() in (C_R, S_R, T_R, D_R) and ch.lower() == H_R)
                or (state.lower() == T_R and ch.lower() == S_R)
            ):
                state += ch
                continue
            elif state.lower() == S_R + H_R and aiueo_idx >= 0:
                if ch.lower() != I_R:
                    ibuf = X_R + Y_R + ch + ibuf
                ibuf = state[:1] + I_R + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() == T_R + S_R and aiueo_idx >= 0:
                if ch.lower() != U_R:
                    ibuf = X_R + ch + ibuf
                ibuf = state[:1] + U_R + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() in (T_R + H_R, D_R + H_R) and aiueo_idx >= 0:
                ibuf = state[:1] + E_R + X_R + Y_R + ch + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() == C_R + H_R and aiueo_idx >= 0:
                if ch.lower() != I_R:
                    ibuf = X_R + Y_R + ch + ibuf
                ibuf = T_R + I_R + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() == Q_R and aiueo_idx >= 0:
                if ch.lower() != U_R:
                    ibuf = X_R + ch + ibuf
                ibuf = K_R + U_R + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() == J_R and aiueo_idx >= 0:
                if ch.lower() != I_R:
                    ibuf = X_R + Y_R + ch + ibuf
                ibuf = Z_R + I_R + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() == F_R and aiueo_idx >= 0:
                if ch.lower() != U_R:
                    ibuf = X_R + ch + ibuf
                ibuf = H_R + U_R + ibuf
                state = EMPTY_STATE
                continue
            elif state.lower() == V_R and aiueo_idx >= 0:
                if ch.lower() != U_R:
                    ibuf = X_R + ch + ibuf
                ibuf = U_R + DAKUTEN_R + ibuf
                state = EMPTY_STATE
                continue
            elif (
                state.lower()
                in (X_R + T_R, L_R + T_R, X_R + T_R + S_R, L_R + T_R + S_R)
                and ch.lower() == U_R
            ):
                ch, state = XTU_K, EMPTY_STATE
                aiueo_idx = -1
            elif state.lower() == Z_R:
                if (state + ch).lower() == HANDAKUTEN_R:
                    ch, state = HANDAKUTEN_K, EMPTY_STATE
                    iueo_idx, punct_idx = -1, -1
                elif (state + ch).lower() == DAKUTEN_R:
                    ch, state = DAKUTEN_K, EMPTY_STATE
                elif ch == MIDDOT_A:
                    ch, state = MIDDOT_K, EMPTY_STATE
                elif ch == HYPHEN_MINUS_A:
                    flags &= 0x7F
                    state = EMPTY_STATE
            if state:
                obuf += state
                ibuf += ch
                state = EMPTY_STATE
                ch, obuf = obuf[:1], obuf[1:]
            else:
                assert state == EMPTY_STATE
                if punct_idx >= 0:
                    ch = PUNCT_K[punct_idx]
                elif ch == CHOUONPU_A:
                    ch = CHOUONPU_K
                elif aiueo_idx >= 0:
                    ch = AIUEO_K[aiueo_idx]
                elif (ch == HYPHEN_MINUS_A) and (flags & 0x80):
                    ch = CHOUONPU_K
                elif ch and (ch.lower() in LEAD_R):
                    state = ch
                    continue
        if ch and ord(ch) < ord(" ") and ch != BACKSPACE_A:
            flags = 0
        else:
            flags = (0x80 if (ch and (ch in ALL_K)) else 0) | (flags >> 1)
        return ch, ibuf, state, obuf, flags


def r2ks(s):
    o = ""

    def getch():
        nonlocal s
        ch, s = s[:1], s[1:]
        return ch

    ibuf, state, obuf, flags = "", EMPTY_STATE, "", 0
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
        __ln="ﾝ",
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
    ln       lla

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
    assert r2ks("Ra-men") == "ﾗｰﾒﾝ"
    assert r2ks("cyocore-to") == "ﾁｮｺﾚｰﾄ"
    assert r2ks("chokore-to") == "ﾁｮｺﾚｰﾄ"
    assert r2ks("tyokore-to") == "ﾁｮｺﾚｰﾄ"
    assert r2ks("tixyokore-to") == "ﾁｮｺﾚｰﾄ"
    assert r2ks("chilyokore-to") == "ﾁｮｺﾚｰﾄ"
    assert r2ks("KYANTO/BAI/MI-/RABU") == "ｷｬﾝﾄ･ﾊﾞｲ･ﾐｰ･ﾗﾌﾞ"
    assert r2ks("byu-t'ifuru/sande-") == "ﾋﾞｭｰﾃｨﾌﾙ･ｻﾝﾃﾞｰ"
    assert r2ks("BarakuZ/Obama") == "ﾊﾞﾗｸ･ｵﾊﾞﾏ"
    assert r2ks("Pa-sonaru/Conpyu-ta-") == "ﾊﾟｰｿﾅﾙ･ｺﾝﾋﾟｭｰﾀｰ"
    assert r2ks("Da/Vinchi=DaVinchi") == "ﾀﾞ･ｳﾞｨﾝﾁ=ﾀﾞｳﾞｨﾝﾁ"
    assert r2ks("VARISU") == "ｳﾞｧﾘｽ"
    assert r2ks("I-SU") == "ｲｰｽ"
    assert r2ks("I^su") == "ｲｰｽ"
    assert r2ks("a-123") == "ｱｰ123"
    assert r2ks("az-123") == "ｱ-123"
    assert r2ks("\b") == "\b"
    assert r2ks("\x7f") == "\x7f"
    assert r2ks("a\b-") == "ｱ\b-"
    assert r2ks("a\x7f-") == "ｱ\x7f-"
    assert r2ks("a -") == "ｱ -"
    assert r2ks("a \b-") == "ｱ \bｰ"
    assert r2ks("a \x7f-") == "ｱ \x7fｰ"
    assert r2ks("a\n\b-") == "ｱ\n\b-"
    assert r2ks("a\r\x7f-") == "ｱ\r\x7f-"
    assert r2ks("k\ba\b-") == "ｱ\b-"
    assert r2ks("k\ba\x7f-") == "ｱ\x7f-"
    assert r2ks("k\ba -") == "ｱ -"
    assert r2ks("k\ba \b-") == "ｱ \bｰ"
    assert r2ks("k\ba \x7f-") == "ｱ \x7fｰ"
    assert r2ks("ak\b\b-") == "ｱ\b-"
    assert r2ks("ak\x7fk\x7f-") == "ｱｰ"
    assert r2ks("a k\b-") == "ｱ -"
    assert r2ks("a k\b\b-") == "ｱ \bｰ"
    assert r2ks("a k\x7f\x7f-") == "ｱ \x7fｰ"
    assert r2ks("k\ba\bk\b-") == "ｱ\b-"
    assert r2ks("k\ba\x7fk\x7f-") == "ｱ\x7f-"
    assert r2ks("k\ba k\b-") == "ｱ -"
    assert r2ks("k\ba \bk\b-") == "ｱ \bｰ"
    assert r2ks("k\ba \x7fk\x7f-") == "ｱ \x7fｰ"
    assert r2ks("ki") == "ｷ"
    assert r2ks("kya") == "ｷｬ"
    assert r2ks("kyu") == "ｷｭ"
    assert r2ks("ya") == "ﾔ"
    assert r2ks("ki\b") == "ｷ\b"
    assert r2ks("kya\b") == "ｷｬ\b"
    assert r2ks("kyu\b") == "ｷｭ\b"
    assert r2ks("ya\b") == "ﾔ\b"
    assert r2ks("\bki") == "\bｷ"
    assert r2ks("\bkya") == "\bｷｬ"
    assert r2ks("\bkyu") == "\bｷｭ"
    assert r2ks("\bya") == "\bﾔ"
    assert r2ks("\bki\b") == "\bｷ\b"
    assert r2ks("\bkya\b") == "\bｷｬ\b"
    assert r2ks("\bkyu\b") == "\bｷｭ\b"
    assert r2ks("\bya\b") == "\bﾔ\b"
    assert r2ks("k\bi") == "ｲ"
    assert r2ks("k\bya") == "ﾔ"
    assert r2ks("ky\ba") == "ｷｧ"  # probably surprising/wrong
    assert r2ks("k\byu") == "ﾕ"
    assert r2ks("ky\bu") == "ｷｩ"  # probably surprising/wrong
    assert r2ks("ky\bya") == "ｷｬ"
    assert r2ks("ky\byu") == "ｷｭ"
    assert r2ks("ky\b\ba") == "ｷｱ"  # probably surprising/wrong
    assert r2ks("ky\b\bu") == "ｷｳ"  # probably surprising/wrong
    assert r2ks("ky\b\bya") == "ｷﾔ"  # probably surprising/wrong
    assert r2ks("ky\b\byu") == "ｷﾕ"  # probably surprising/wrong
    assert r2ks("ﾌ-") == "ﾌｰ"
    assert r2ks("fu-") == "ﾌｰ"
    assert r2ks("f\b-") == "-"
    assert r2ks("f\bu") == "ｳ"
    assert r2ks("qu") == "ｸ"
    assert r2ks("q\bu") == "ｳ"
    assert r2ks("kwu") == "ｸｩ"
    assert r2ks("kw\bu") == "ｸｳ"  # probably surprising/wrong
    assert r2ks("konnnichiha") == "ｺﾝﾆﾁﾊ"
    assert r2ks("kon'nichiha") == "ｺﾝﾆﾁﾊ"
    assert r2ks("kon'nitiha") == "ｺﾝﾆﾁﾊ"
    assert r2ks("colnnitiha") == "ｺﾝﾆﾁﾊ"
    assert r2ks("coxnnitiha") == "ｺﾝﾆﾁﾊ"
    assert r2ks("wwhawwhiwwhuwwhewwho") == "ｯｳｧｯｳｨｯｳｯｳｪｯｳｫ"
    assert r2ks("vvavvivvuvvevvo") == "ｯｳﾞｧｯｳﾞｨｯｳﾞｯｳﾞｪｯｳﾞｫ"
    assert r2ks("ttyattyittyuttyettyo") == "ｯﾁｬｯﾁｨｯﾁｭｯﾁｪｯﾁｮ"
    assert r2ks("ccyaccyiccyuccyeccyo") == "ｯﾁｬｯﾁｨｯﾁｭｯﾁｪｯﾁｮ"
    assert r2ks("ffaffiffuffeffo") == "ｯﾌｧｯﾌｨｯﾌｯﾌｪｯﾌｫ"
    assert r2ks("bbabbibbubbebbo") == "ｯﾊﾞｯﾋﾞｯﾌﾞｯﾍﾞｯﾎﾞ"
    assert r2ks("pphapphipphuppheppho") == "ｯﾌﾟｧｯﾌﾟｨｯﾌﾟｩｯﾌﾟｪｯﾌﾟｫ"
    assert r2ks("bbyabbyibbyubbyebbyo") == "ｯﾋﾞｬｯﾋﾞｨｯﾋﾞｭｯﾋﾞｪｯﾋﾞｮ"
    assert r2ks("ppyappyippyuppyeppyo") == "ｯﾋﾟｬｯﾋﾟｨｯﾋﾟｭｯﾋﾟｪｯﾋﾟｮ"
    assert r2ks("pphapphipphuppheppho") == "ｯﾌﾟｧｯﾌﾟｨｯﾌﾟｩｯﾌﾟｪｯﾌﾟｫ"

smoketest()

import sys
import unicodedata


def main():
    """
    When invoked with no arguments, this acts as a filter from stdin to stdout.
    When invoked with arguments, each is treated as a filename and filtered to stdout.
    The special filename `-` refers to stdin.
    """
    ibuf, state, obuf, flags = "", EMPTY_STATE, "", 0
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
