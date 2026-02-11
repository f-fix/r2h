#!/usr/bin/env python3

"""
this is a (terrible) converter from word processor-like romaji to halfwidth katakana

- `-`: convert to chouonpu (only immediately after kana!)
- `^`: convert to chouonpu
- `z;`: convert to dakuten
- `z:`: convert to handakuten
- `z/`: convert to middle dot
- `.`: convert to ideographic full stop
- `,`: convert to ideographic comma
- `[`: convert to left corner bracket
- `]`: convert to right corner bracket
- `z-`: convert to hyphen-minus

ASCII backspace (Ctrl-H, 0x08) and Delete/Rubout (Ctrl-?, 0x7F) can erase parts of in-progress conversions. When no conversion is in progress, they will back up the is-it-kana state used to determine `-` behavior, but this only remembers the most recent 8 characters. Any other ASCII control character will cause the kana state history to be cleared, though.

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
11. write `du` (or `dzu`) for the voiced version of `tsu`/`tu`; `zu` is voiced `su`
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

R2K_ONE_TO_ONE_IMPLEMENTATION = (  # either "fast" or "simple" (constant, ignored after time of import)
    "simple"
)


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
WO_R = "wo"
X_K = "ｧｨｩｪｫ"
XYAYUYO_K = "ｬｭｮ"
XY_R = "xy"
XTU_K = "ｯ"
XTU_R = "xtu"
AIUEO_R = "aiueo"
AIUEO_R_SET = frozenset(AIUEO_R)
AIUEO_K = "ｱｲｳｴｵ"
U_K = AIUEO_K[2]
AUO_R = "auo"
AUO_R_SET = frozenset(AUO_R)
KSTNHMR_R = "kstnhmr"
K_K = "ｶｷｸｹｺ"
S_K = "ｻｼｽｾｿ"
T_K = "ﾀﾁﾂﾃﾄ"
TU_K = T_K[2]
N_K = "ﾅﾆﾇﾈﾉ"
H_K = "ﾊﾋﾌﾍﾎ"
HU_K = H_K[2]
M_K = "ﾏﾐﾑﾒﾓ"
YAYUYO_K = "ﾔﾕﾖ"
R_K = "ﾗﾘﾙﾚﾛ"
XKSTNHMR_R = "x" + KSTNHMR_R
XKSTNHMR_K = [X_K, K_K, S_K, T_K, N_K, H_K, M_K, R_K]
WA_K = "ﾜ"
WA_R = "wa"
NN_K = "ﾝ"
NN_R = "n'"
DAKUTEN_K = "ﾞ"
DAKUTEN_R = "z;"
HANDAKUTEN_K = "ﾟ"
HANDAKUTEN_R = "z:"
YWZ_R = "ywz"
LEAD_R = XKSTNHMR_R + YWZ_R
EXTRA_LEAD_R2R_R = "lvgqcjdbfp"
LEAD_R2R_R_SET = frozenset(LEAD_R + EXTRA_LEAD_R2R_R)
LEAD_Y_R2R_R_SET = frozenset("xlvjnbmrkgqzhfsctdp") | frozenset({"hw", "t'", "d'"})
LEAD_W_R2R_R_SET = frozenset("kgqzhfsctd")
LEAD_H_R2R_R_SET = frozenset("sctdpw")
LEAD_AIUEO_R2R_R_SET = frozenset("kgcsztdnhbpmr")
ONSET_I_AIUEO_R2R_R_SET = frozenset(
    {
        "ky",
        "gy",
        "zy",
        "jy",
        "ty",
        "dy",
        "ny",
        "by",
        "my",
        "ry",
        "hy",
        "py",
    }
)
ONSET_U_AIUEO_R_SET = frozenset(
    {
        "kw",
        "gw",
        "cw",
        "qw",
        "sw",
        "zw",
        "fw",
        "ph",
    }
)
ONSET_U_AIEO_R_SET = frozenset({"q", "ts", "dz", "hw", "f"})
ONSET_DEVOICING_MAP = dict(
    l="x",
    v="u",
    q="k",
    g="k",
    z="s",
    j="s",
    d="t",
    f="h",
    b="h",
    p="h",
)
HAS_DAKUTEN_R_SET = frozenset("vgjzdb")
HAS_HANDAKUTEN_R_SET = frozenset("p")
ALL_R = AIUEO_R + XKSTNHMR_R + YWZ_R + EXTRA_LEAD_R2R_R
assert sorted(ALL_R) == [chr(cc) for cc in range(ord("a"), 1 + ord("z"))]

ALL_K = (  # this is ordered according to the kana layout of the single-byte part of CP932
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
assert ALL_K == bytes(
    range(0xA1, 0xE0)
).decode(  # Ensure all the halfwidth kana are represented and each only once, and in encoded order
    "cp932"
)

ALL_1_1_STARTS_R = (  # this is ordered according to the kana layout of the single-byte part of CP932
    [punct for punct in PUNCT_A]
    + [WO_R, "x", XY_R, XTU_R, CHOUONPU_A]
    + [vowel for vowel in AIUEO_R]
    + [onset for onset in KSTNHMR_R if onset != "r"]
    + [
        "y",
        "r",
        WA_R,
        NN_R,
        DAKUTEN_R,
        HANDAKUTEN_R,
    ]
)


def expand_1_1_starts(*starts):
    """
    used to reduce the "ROM" size for simple 1:1 romaji
    """
    expanded = []
    for start in starts:
        if start in XKSTNHMR_R:
            for vowel in AIUEO_R:
                expanded += [start + vowel]
        elif start in (XY_R, "y"):
            for vowel in AUO_R:
                expanded += [start + vowel]
        else:
            expanded += [start]
    return expanded


def r2k_one_to_one_simple(*, ibuf, state, obuf, flags, getch):
    """
    convert subset of romaji to halfwidth katakana.
    [simpler but slower version]

    - ibuf is an input stuffing buffer used when retrying characters from failed conversions; initially it should be an empty string.
    - state is the current state of the input conversion; initially it should be "".
    - obuf is a buffer for accumulating characters to be output; initially it should be an empty string.
    - flags is an integer containing conversion state flags relating to backspace processing; initially it should be 0.
    - getch is a callable closure or function that returns a single character from the input stream when called, blocking if needed; returning an empty sttring indicates the input source is exhausted (EOF).

    the return values are ch, ibuf, state, obuf, flags.
    - ch is the next output character, or an empty string to indicate that the input source is exhausted (EOF) and all input fully processed.
    - the returned ibuf, state, obuf, and flags should be passed back in on a subsequent call associated with the same input source / getch.

    this is the second phase with no support for romaji-to-romaji rewriting or alternate spellings.

    this only supports a romaji subset that maps 1:1 to halfwidth kana characters.

    this only supports one spelling for each character in the halfwidth kana character set.

    supported inputs:

    ```
        a  i  u  e  o        ｱ  ｲ  ｳ  ｴ  ｵ
       ka ki ku ke ko        ｶ  ｷ  ｸ  ｹ  ｺ
       sa si su se so        ｻ  ｼ  ｽ  ｾ  ｿ
       ta ti tu te to        ﾀ  ﾁ  ﾂ  ﾃ  ﾄ
       na ni nu ne no        ﾅ  ﾆ  ﾇ  ﾈ  ﾉ
       ha hi hu he ho        ﾊ  ﾋ  ﾌ  ﾍ  ﾎ
       ma mi mu me mo        ﾏ  ﾐ  ﾑ  ﾒ  ﾓ
       ya    yu    yo        ﾔ     ﾕ     ﾖ
       ra ri ru re ro        ﾗ  ﾘ  ﾙ  ﾚ  ﾛ
       wa          wo        ﾜ           ｦ
      xya   xyu   xyo        ｬ     ｭ     ｮ     (small versions of ya/yu/yo)
       xa xi xu xe xo        ｧ  ｨ  ｩ  ｪ  ｫ     (small versions of a/i/u/e/o)
            xtu                    ｯ           (small tsu)
             n'                    ﾝ           (moraic n)

       ^                     ｰ                 (chouonpu)
       -                     ｰ or -            (contextual: chouonpu after kana, hyphen-minus elsewhere)
       z;                    ﾞ                 (dakuten)
       z:                    ﾟ                 (handakuten)
       z-                    -                 (hyphen-minus)
       z/ or /               ･                 (middle dot; exception to the only-one-spelling rule)
       .                     ｡                 (ideographic full stop)
       ,                     ､                 (ideographic comma)
       [                     ｢                 (left corner bracket)
       ]                     ｣                 (right corner bracket)

    ```

    ASCII backspace (Ctrl-H, 0x08) and Delete/Rubout (Ctrl-?, 0x7F) can erase parts of in-progress conversions.

    """
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
            nstate = ""
            lstate, lch = state.lower(), ch.lower()
            lstate_ch = lstate + lch
            cc = 0xA1
            matched = False
            for start in ALL_1_1_STARTS_R:
                for romaji in expand_1_1_starts(start):
                    if lstate_ch == romaji:
                        ch = ALL_K[cc - 0xA1]  # a.k.a. bytes([cc]).decode("cp932")
                        state = ""
                        nstate = ""
                        matched = True
                        break
                    elif ch and romaji.startswith(lstate_ch):
                        nstate = state + ch
                    cc += 1
                if matched:
                    break
            if nstate:
                state = nstate
                continue
            elif matched:
                pass
            elif (lstate == "z") and (ch == MIDDOT_A):
                ch, state = MIDDOT_K, ""
            elif (lstate == "z") and (ch == HYPHEN_MINUS_A):
                flags &= 0x7F
                state = ""
            elif (ch == HYPHEN_MINUS_A) and (flags & 0x80):
                ch = CHOUONPU_K
            if state:
                obuf += state[:1]
                ibuf += state[1:] + ch
                state = ""
                ch, obuf = obuf[:1], obuf[1:]
        if ch and ord(ch) < ord(" ") and ch != BACKSPACE_A:
            flags = 0
        else:
            flags = (0x80 if (ch and (ch in ALL_K)) else 0) | (flags >> 1)
        return ch, ibuf, state, obuf, flags


def r2k_one_to_one_fast(*, ibuf, state, obuf, flags, getch):
    """
    convert subset of romaji to halfwidth katakana.
    [faster but larger version]

    - ibuf is an input stuffing buffer used when retrying characters from failed conversions; initially it should be an empty string.
    - state is the current state of the input conversion; initially it should be "".
    - obuf is a buffer for accumulating characters to be output; initially it should be an empty string.
    - flags is an integer containing conversion state flags relating to backspace processing; initially it should be 0.
    - getch is a callable closure or function that returns a single character from the input stream when called, blocking if needed; returning an empty sttring indicates the input source is exhausted (EOF).

    the return values are ch, ibuf, state, obuf, flags.
    - ch is the next output character, or an empty string to indicate that the input source is exhausted (EOF) and all input fully processed.
    - the returned ibuf, state, obuf, and flags should be passed back in on a subsequent call associated with the same input source / getch.

    this is the second phase with no support for romaji-to-romaji rewriting or alternate spellings.

    this only supports a romaji subset that maps 1:1 to halfwidth kana characters.

    this only supports one spelling for each character in the halfwidth kana character set.

    supported inputs:

    ```
        a  i  u  e  o        ｱ  ｲ  ｳ  ｴ  ｵ
       ka ki ku ke ko        ｶ  ｷ  ｸ  ｹ  ｺ
       sa si su se so        ｻ  ｼ  ｽ  ｾ  ｿ
       ta ti tu te to        ﾀ  ﾁ  ﾂ  ﾃ  ﾄ
       na ni nu ne no        ﾅ  ﾆ  ﾇ  ﾈ  ﾉ
       ha hi hu he ho        ﾊ  ﾋ  ﾌ  ﾍ  ﾎ
       ma mi mu me mo        ﾏ  ﾐ  ﾑ  ﾒ  ﾓ
       ya    yu    yo        ﾔ     ﾕ     ﾖ
       ra ri ru re ro        ﾗ  ﾘ  ﾙ  ﾚ  ﾛ
       wa          wo        ﾜ           ｦ
      xya   xyu   xyo        ｬ     ｭ     ｮ     (small versions of ya/yu/yo)
       xa xi xu xe xo        ｧ  ｨ  ｩ  ｪ  ｫ     (small versions of a/i/u/e/o)
            xtu                    ｯ           (small tsu)
             n'                    ﾝ           (moraic n)

       ^                     ｰ                 (chouonpu)
       -                     ｰ or -            (contextual: chouonpu after kana, hyphen-minus elsewhere)
       z;                    ﾞ                 (dakuten)
       z:                    ﾟ                 (handakuten)
       z-                    -                 (hyphen-minus)
       z/ or /               ･                 (middle dot; exception to the only-one-spelling rule)
       .                     ｡                 (ideographic full stop)
       ,                     ､                 (ideographic comma)
       [                     ｢                 (left corner bracket)
       ]                     ｣                 (right corner bracket)

    ```

    ASCII backspace (Ctrl-H, 0x08) and Delete/Rubout (Ctrl-?, 0x7F) can erase parts of in-progress conversions.

    """
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
            auo_idx = AUO_R.find(ch.lower()) if ch else -1
            punct_idx = PUNCT_A.find(ch.lower()) if ch else -1
            state_xkstnhmr_idx = XKSTNHMR_R.find(state.lower()) if state else -1
            if (state.lower() == "n") and (ch.lower() == "'"):
                ch, state = NN_K, ""
            elif (state.lower() == "xy") and (auo_idx >= 0):
                ch, state = XYAYUYO_K[auo_idx], ""
                aiueo_idx = -1
            elif (state_xkstnhmr_idx >= 0) and (aiueo_idx >= 0):
                ch, state = (
                    XKSTNHMR_K[state_xkstnhmr_idx][aiueo_idx],
                    "",
                )
                aiueo_idx = -1
            elif state.lower() == "y" and (auo_idx >= 0):
                ch, state = YAYUYO_K[auo_idx], ""
                aiueo_idx = -1
            elif state.lower() == "w" and ch.lower() == "a":
                ch = WA_K
                state = ""
                aiueo_idx = -1
            elif state.lower() == "w" and ch.lower() == "o":
                ch = WO_K
                state = ""
                aiueo_idx = -1
            elif (state.lower() == "x") and ch.lower() in ("y", "t"):
                state += ch
                continue
            elif state.lower() == "xt" and ch.lower() == "u":
                ch, state = XTU_K, ""
                aiueo_idx = -1
            elif (state + ch).lower() == HANDAKUTEN_R:
                ch, state = HANDAKUTEN_K, ""
                iueo_idx, punct_idx = -1, -1
            elif (state + ch).lower() == DAKUTEN_R:
                ch, state = DAKUTEN_K, ""
            elif (state.lower() == "z") and (ch == MIDDOT_A):
                ch, state = MIDDOT_K, ""
            elif (state.lower() == "z") and (ch == HYPHEN_MINUS_A):
                flags &= 0x7F
                state = ""
            if state:
                obuf += state[:1]
                ibuf += state[1:] + ch
                state = ""
                ch, obuf = obuf[:1], obuf[1:]
            else:
                assert state == ""
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


r2k_one_to_one = dict(fast=r2k_one_to_one_fast, simple=r2k_one_to_one_simple)[
    R2K_ONE_TO_ONE_IMPLEMENTATION
]

UNUSED_R2R = chr(
    0x10FFFF
)  # used as a marker for unused/filler slots in various character buffers


def r2h(*, ibuf, state, obuf, flags, getch):
    """
    convert romaji to halfwidth katakana

    - ibuf is an input stuffing buffer used when retrying characters from failed conversions; initially it should be an empty string.
    - state is the current state of the input conversion; initially it should be "".
    - obuf is a buffer for accumulating characters to be output; initially it should be an empty string.
    - flags is an integer containing conversion state flags relating to backspace processing; initially it should be 0.
    - getch is a callable closure or function that returns a single character from the input stream when called, blocking if needed; returning an empty sttring indicates the input source is exhausted (EOF).

    the return values are ch, ibuf, state, obuf, flags.
    - ch is the next output character, or an empty string to indicate that the input source is exhausted (EOF) and all input fully processed.
    - the returned ibuf, state, obuf, and flags should be passed back in on a subsequent call associated with the same input source / getch.

    supported inputs:

    ```
     a  i  u  e  o  ya  yi  yu  ye  yo    ｱ   ｲ   ｳ   ｴ   ｵ  ﾔ   ｲ   ﾕ   ｲｪ  ﾖ
    ka ki ku ke ko kya kyi kyu kye kyo    ｶ   ｷ   ｸ   ｹ   ｺ  ｷｬ  ｷｨ  ｷｭ  ｷｪ  ｷｮ
    sa si su se so sya syi syu sye syo    ｻ   ｼ   ｽ   ｾ   ｿ  ｼｬ  ｼｨ  ｼｭ  ｼｪ  ｼｮ
    ta ti tu te to tya tyi tyu tye tyo    ﾀ   ﾁ   ﾂ   ﾃ   ﾄ  ﾁｬ  ﾁｨ  ﾁｭ  ﾁｪ  ﾁｮ
    na ni nu ne no nya nyi nyu nye nyo    ﾅ   ﾆ   ﾇ   ﾈ   ﾉ  ﾆｬ  ﾆｨ  ﾆｭ  ﾆｪ  ﾆｮ
    ha hi hu he ho hya hyi hyu hye hyo    ﾊ   ﾋ   ﾌ   ﾍ   ﾎ  ﾋｬ  ﾋｨ  ﾋｭ  ﾋｪ  ﾋｮ
    ma mi mu me mo mya myi myu mye myo    ﾏ   ﾐ   ﾑ   ﾒ   ﾓ  ﾐｬ  ﾐｨ  ﾐｭ  ﾐｪ  ﾐｮ
    ra ri ru re ro rya ryi ryu rye ryo    ﾗ   ﾘ   ﾙ   ﾚ   ﾛ  ﾘｬ  ﾘｨ  ﾘｭ  ﾘｪ  ﾘｮ
    wa wi wu we wo                        ﾜ   ｳｨ  ｳ   ｳｪ  ｦ

    ga gi gu ge go gya gyi gyu gye gyo    ｶﾞ  ｷﾞ  ｸﾞ  ｹﾞ  ｺﾞ ｷﾞｬ ｷﾞｨ ｷﾞｭ ｷﾞｪ ｷﾞｮ
    za zi zu ze zo zya zyi zyu zye zyo    ｻﾞ  ｼﾞ  ｽﾞ  ｾﾞ  ｿﾞ ｼﾞｬ ｼﾞｨ ｼﾞｭ ｼﾞｪ ｼﾞｮ
    da di du de do dya dyi dyu dye dyo    ﾀﾞ  ﾁﾞ  ﾂﾞ  ﾃﾞ  ﾄﾞ ﾁﾞｬ ﾁﾞｨ ﾁﾞｭ ﾁﾞｪ ﾁﾞｮ
    ba bi bu be bo bya byi byu bye byo    ﾊﾞ  ﾋﾞ  ﾌﾞ  ﾍﾞ  ﾎﾞ ﾋﾞｬ ﾋﾞｨ ﾋﾞｭ ﾋﾞｪ ﾋﾞｮ
    pa pi pu pe po pya pyi pyu pye pyo    ﾊﾟ  ﾋﾟ  ﾌﾟ  ﾍﾟ  ﾎﾟ ﾋﾟｬ ﾋﾟｨ ﾋﾟｭ ﾋﾟｪ ﾋﾟｮ

      wha  whi  whu  whe  who             ｳｧ  ｳｨ  ｳ   ｳｪ  ｳｫ
      kwa  kwi  kwu  kwe  kwo             ｸｧ  ｸｨ  ｸｩ  ｸｪ  ｸｫ
       qa   qi   qu   qe   qo             ｸｧ  ｸｨ  ｸ   ｸｪ  ｸｫ
      qya       qyu       qyo             ｸｬ      ｸｭ      ｸｮ
      qwa  qwi  qwu  qwe  qwo             ｸｧ  ｸｨ  ｸｩ  ｸｪ  ｸｫ
      cwa  cwi  cwu  cwe  cwo             ｸｧ  ｸｨ  ｸｩ  ｸｪ  ｸｫ
       ca   ci   cu   ce   co             ｶ   ｼ   ｸ   ｾ   ｺ
      cya  cyi  cyu  cye  cyo             ﾁｬ  ﾁｨ  ﾁｭ  ﾁｪ  ﾁｮ
      sha  shi  shu  she  sho             ｼｬ  ｼ   ｼｭ  ｼｪ  ｼｮ
      swa  swi  swu  swe  swo             ｽｧ  ｽｨ  ｽｩ  ｽｪ  ｽｫ
      cha  chi  chu  che  cho             ﾁｬ  ﾁ   ﾁｭ  ﾁｪ  ﾁｮ
      tsa  tsi  tsu  tse  tso             ﾂｧ  ﾂｨ  ﾂ   ﾂｪ  ﾂｫ
      tha  thi  thu  the  tho             ﾃｬ  ﾃｨ  ﾃｭ  ﾃｪ  ﾃｮ
      twa  twi  twu  twe  two             ﾄｧ  ﾄｨ  ﾄｩ  ﾄｪ  ﾄｫ
           t'i  t'u                           ﾃｨ  ﾄｩ
                t'yu                              ﾃｭ
       fa   fi   fu   fe   fo             ﾌｧ  ﾌｨ  ﾌ   ﾌｪ  ﾌｫ
      fya       fyu       fyo             ﾌｬ      ﾌｭ      ﾌｮ
      hwa  hwi       hwe  hwo             ﾌｧ  ﾌｨ      ﾌｪ  ﾌｫ
               hwyu                               ﾌｭ
      fwa  fwi  fwu  fwe  fwo             ﾌｧ  ﾌｨ  ﾌｩ  ﾌｪ  ﾌｫ

       va   vi   vu   ve   vo             ｳﾞｧ ｳﾞｨ ｳﾞ  ｳﾞｪ ｳﾞｫ
      vya  vyi  vyu  vye  vyo             ｳﾞｬ ｳﾞｨ ｳﾞｭ ｳﾞｪ ｳﾞｮ
      gwa  gwi  gwu  gwe  gwo             ｸﾞｧ ｸﾞｨ ｸﾞｩ ｸﾞｪ ｸﾞｫ
       ja   ji   ju   je   jo             ｼﾞｬ ｼﾞ  ｼﾞｭ ｼﾞｪ ｼﾞｮ
      jya  jyi  jyu  jye  jyo             ｼﾞｬ ｼﾞｨ ｼﾞｭ ｼﾞｪ ｼﾞｮ
      zwa  zwi  zwu  zwe  zwo             ｽﾞｧ ｽﾞｨ ｽﾞｩ ｽﾞｪ ｽﾞｫ
      dza  dzi  dzu  dze  dzo             ﾂﾞｧ ﾂﾞｨ ﾂﾞ  ﾂﾞｪ ﾂﾞｫ
      dha  dhi  dhu  dhe  dho             ﾃﾞｬ ﾃﾞｨ ﾃﾞｭ ﾃﾞｪ ﾃﾞｮ
      dwa  dwi  dwu  dwe  dwo             ﾄﾞｧ ﾄﾞｨ ﾄﾞｩ ﾄﾞｪ ﾄﾞｫ
           d'i  d'u                           ﾃﾞｨ ﾄﾞｩ
               d'yu                               ﾃﾞｭ
      pha  phi  phu  phe  pho             ﾌﾟｧ ﾌﾟｨ ﾌﾟｩ ﾌﾟｪ ﾌﾟｫ

       xa   xi   xu   xe   xo             ｧ   ｨ   ｩ   ｪ   ｫ (small versions of a/i/u/e/o)
      xya  xyi  xyu  xye  xyo             ｬ   ｨ   ｭ   ｪ   ｮ (small versions of ya/i/yu/e/yo)
                xtu                               ｯ         (small tsu)
               xtsu                               ｯ         (small tsu)
       la   li   lu   le   lo             ｧ   ｨ   ｩ   ｪ   ｫ (small versions of a/i/u/e/o)
      lya  lyi  lyu  lye  lyo             ｬ   ｨ   ｭ   ｪ   ｮ (small versions of ya/i/yu/e/yo)
                ltu                               ｯ         (small tsu)
               ltsu                               ｯ         (small tsu)
       (repeated consonant other than n)          ｯ         (small tsu for all but the final instance)
       n' or nn or xn or ln or n                  ﾝ         (moraic n)
       ^                                  ｰ                 (chouonpu)
       -                                  ｰ or -            (contextual: chouonpu after kana, hyphen-minus elsewhere)
       z;                                 ﾞ                 (dakuten)
       z:                                 ﾟ                 (handakuten)
       z-                                 -                 (hyphen-minus)
       z/ or /                            ･                 (middle dot)
       .                                  ｡                 (ideographic full stop)
       ,                                  ､                 (ideographic comma)
       [                                  ｢                 (left corner bracket)
       ]                                  ｣                 (right corner bracket)

    ```

    ASCII backspace (Ctrl-H, 0x08) and Delete/Rubout (Ctrl-?, 0x7F) can erase parts of in-progress conversions.

    """
    ibuf_r2k, ibuf_r2r = ibuf[::2].rstrip(UNUSED_R2R), ibuf[1::2].rstrip(UNUSED_R2R)
    state_r2k, prefix = state[::2].rstrip(UNUSED_R2R), state[1::2].rstrip(UNUSED_R2R)
    obuf_r2k, obuf_r2r = obuf[::2].rstrip(UNUSED_R2R), obuf[1::2].rstrip(UNUSED_R2R)
    flags_r2k, flags_r2r = flags & 0xFF, flags >> 8

    def getch_r2r():
        """
        romaji-to-romaji rewriting
        """
        nonlocal ibuf_r2r, prefix, obuf_r2r, flags_r2r
        while True:
            if obuf_r2r:
                ch, obuf_r2r = obuf_r2r[:1], obuf_r2r[1:]
                break
            if ibuf_r2r:
                ch, ibuf_r2r = ibuf_r2r[:1], ibuf_r2r[1:]
            else:
                ch = getch()
            lch = ch.lower()
            lprefix = prefix.lower()
            lprefix_ch = lprefix + lch
            if prefix and (lch in (BACKSPACE_A, RUBOUT_A)):
                prefix = prefix[:-1]
                continue

            def cased(s):
                if prefix != lprefix:
                    s = s.upper()
                return s

            voicing_r = ""
            if lprefix[:1] in HAS_DAKUTEN_R_SET:
                voicing_r = cased(DAKUTEN_R)
            elif lprefix[:1] in HAS_HANDAKUTEN_R_SET:
                voicing_r = cased(HANDAKUTEN_R)
            onset_r = prefix[:1]
            onset_r = cased(ONSET_DEVOICING_MAP.get(onset_r.lower(), "")) or onset_r
            if lprefix_ch[:2] == "wh":
                onset_r = cased("u")
            elif lprefix[:1] == "c":
                if (lprefix[1:2] or lch) in ("i", "e"):
                    onset_r = cased("s")
                elif (lprefix[1:2] or lch) in ("h", "y"):
                    onset_r = cased("t")
                else:
                    onset_r = cased("k")
            onset_ch_r = onset_r + ch + voicing_r
            onset_i_r = onset_r + cased("i") + voicing_r
            onset_u_r = onset_r + cased("u") + voicing_r
            onset_e_r = onset_r + cased("e") + voicing_r
            onset_o_r = onset_r + cased("o") + voicing_r
            small_r = cased("x")
            small_y_r = small_r + cased("y")
            if prefix and (lprefix != "n") and (lch == lprefix):
                obuf_r2r = small_r + cased("tu")
                prefix = ch
                continue
            if (
                (prefix == "" and lch in LEAD_R2R_R_SET)
                or ((lprefix in ("x", "l")) and (lch == "t"))
                or ((lprefix in LEAD_Y_R2R_R_SET) and (lch == "y"))
                or ((lprefix in ("xt", "lt", "t")) and (lch == "s"))
                or ((lprefix in LEAD_W_R2R_R_SET) and (lch == "w"))
                or ((lprefix in LEAD_H_R2R_R_SET) and (lch == "h"))
                or ((lprefix in ("t", "d")) and lch == "'")
                or ((lprefix == "d") and lch == "z")
            ):
                prefix += ch
                continue
            elif ((lprefix in ("x", "l")) and lch in AIUEO_R_SET) or (
                (lprefix in ("xy", "ly")) and (lch in ("i", "e"))
            ):
                obuf_r2r = small_r + ch
                prefix = ""
                continue
            elif (lprefix in ("x", "l")) and lch == "n":
                obuf_r2r = ch + "'"
                prefix = ""
                continue
            elif (lprefix in ("xy", "ly")) and lch in AUO_R_SET:
                obuf_r2r = small_y_r + ch
                prefix = ""
                continue
            elif ((lprefix in ("xt", "lt")) and (lch == "u")) or (
                (lprefix in ("xts", "lts")) and (lch == "u")
            ):
                obuf_r2r = small_r + prefix[1:2] + ch
                prefix = ""
                continue
            elif (lprefix == "v") and (lch == "u"):
                obuf_r2r = onset_r + voicing_r
                prefix = ""
                continue
            elif (
                ((lprefix == "v") and (lch in AIUEO_R_SET) and (lch != "u"))
                or ((lprefix == "vy") and (lch in ("i", "e")))
                or ((lprefix == "wh") and lch in AIUEO_R_SET and (lch != "u"))
            ):
                obuf_r2r = onset_r + voicing_r + small_r + ch
                prefix = ""
                continue
            elif (lprefix == "vy") and lch in AUO_R_SET:
                obuf_r2r = onset_r + voicing_r + small_r + prefix[1:] + ch
                prefix = ""
                continue
            elif (
                ((lprefix in LEAD_AIUEO_R2R_R_SET) and (lch in AIUEO_R_SET))
                or ((lprefix == "y") and lch in AUO_R_SET)
                or ((lprefix == "w") and (lch in ("a", "o")))
                or ((lprefix == "q") and (lch == "u"))
                or ((lprefix in ("ch", "cy")) and (lch == "i"))
                or ((lprefix in ("sh", "j")) and (lch == "i"))
            ):
                obuf_r2r = onset_ch_r
                if lprefix == "cy":
                    obuf_r2r += small_r + ch
                prefix = ""
                continue
            elif (lprefix in ONSET_I_AIUEO_R2R_R_SET) and (lch in AUO_R_SET):
                obuf_r2r = onset_i_r
                obuf_r2r += small_r + prefix[1:] + ch
                prefix = ""
                continue
            elif (lprefix in ONSET_I_AIUEO_R2R_R_SET) and (lch in ("i", "e")):
                obuf_r2r = onset_i_r
                obuf_r2r += small_r + ch
                prefix = ""
                continue
            elif (
                ((lprefix in ONSET_U_AIUEO_R_SET) and (lch in AIUEO_R_SET))
                or (
                    (lprefix in ONSET_U_AIEO_R_SET)
                    and (lch in AIUEO_R_SET)
                    and lch != "u"
                )
                or ((lprefix == "hwy") and (lch == "u"))
            ):
                obuf_r2r = onset_u_r + small_r + prefix[2:] + ch
                prefix = ""
                continue
            elif (lprefix in ("ts", "dz", "f")) and (lch == "u"):
                obuf_r2r = onset_u_r
                prefix = ""
                continue
            elif (lprefix in ("qy", "fy")) and lch in AUO_R_SET:
                obuf_r2r = onset_u_r + small_r + prefix[1:] + ch
                prefix = ""
                continue
            elif ((lprefix in ("ch", "cy")) and (lch in AUO_R_SET)) or (
                (lprefix in ("sh", "sy", "j")) and (lch in AUO_R_SET)
            ):
                obuf_r2r = onset_i_r + small_y_r + ch
                prefix = ""
                continue
            elif ((lprefix in ("ch", "cy")) and (lch == "e")) or (
                (lprefix in ("sh", "sy", "j"))
                and ((lch == "i" and lprefix == "sy") or lch == "e")
            ):
                obuf_r2r = onset_i_r + small_r + ch
                prefix = ""
                continue
            elif (lprefix == "z") and (
                lprefix_ch
                in (
                    DAKUTEN_R,
                    HANDAKUTEN_R,
                    "z" + MIDDOT_A,
                    "z" + HYPHEN_MINUS_A,
                )
            ):
                obuf_r2r = prefix + ch
                prefix = ""
                continue
            elif (lprefix in ("th", "dh")) and lch in AUO_R_SET:
                obuf_r2r = onset_e_r
                obuf_r2r += small_y_r + ch
                prefix = ""
                continue
            elif (lprefix in ("th", "dh")) and lch in ("i", "e"):
                obuf_r2r = onset_e_r
                obuf_r2r += small_r + ch
                prefix = ""
                continue
            elif ((lprefix in ("tw", "dw")) and lch in AIUEO_R_SET) or (
                (lprefix in ("t'", "d'")) and (lch == "u")
            ):
                obuf_r2r = onset_o_r + small_r + ch
                prefix = ""
                continue
            elif ((lprefix in ("t'", "d'")) and (lch == "i")) or (
                (
                    lprefix
                    in (
                        "t'y",
                        "d'y",
                    )
                )
                and (lch == "u")
            ):
                obuf_r2r = onset_e_r + small_r + prefix[2:] + ch
                prefix = ""
                continue
            elif (lprefix == "n") and (lch in ("n", "'")):
                obuf_r2r = onset_r + "'"
                prefix = ""
                continue
            elif (lprefix == "n") and (
                (not ch) or ((lch not in AIUEO_R_SET) and (lch not in ("n", "'")))
            ):
                obuf_r2r = onset_r + "'"
                prefix = ""
                ibuf_r2r = ch + ibuf_r2r
                continue
            elif (
                ((lprefix == "y") and (lch == "i"))
                or ((lprefix == "w") and (lch == "u"))
                or ((lprefix == "wh") and (lch == "u"))
            ):
                obuf_r2r = ch
                prefix = ""
                continue
            elif (lprefix == "y") and (lch == "e"):
                obuf_r2r = cased("i") + small_r + ch
                prefix = ""
                continue
            elif (lprefix == "w") and (lch in ("i", "e")):
                obuf_r2r = cased("u") + small_r + ch
                prefix = ""
                continue
            if prefix:
                # print(f"r2r fallback!!! {dict(prefix=prefix, ch=ch)}")
                obuf_r2r = prefix[:1]
                ibuf_r2r = prefix[1:] + ch + ibuf_r2r
                prefix = ""
                continue
            break
        return ch

    ch, ibuf_r2k, state_r2k, obuf_r2k, flags_r2k = r2k_one_to_one(
        ibuf=ibuf_r2k, state=state_r2k, obuf=obuf_r2k, flags=flags_r2k, getch=getch_r2r
    )
    ibuf = "".join(
        [
            (ibuf_r2k[i : 1 + i] or UNUSED_R2R) + (ibuf_r2r[i : 1 + i] or UNUSED_R2R)
            for i in range(max(len(ibuf_r2k), len(ibuf_r2r)))
        ]
    )
    state = "".join(
        [
            (state_r2k[i : 1 + i] or UNUSED_R2R) + (prefix[i : 1 + i] or UNUSED_R2R)
            for i in range(max(len(state_r2k), len(prefix)))
        ]
    )
    obuf = "".join(
        [
            (obuf_r2k[i : 1 + i] or UNUSED_R2R) + (obuf_r2r[i : 1 + i] or UNUSED_R2R)
            for i in range(max(len(obuf_r2k), len(obuf_r2r)))
        ]
    )
    flags = flags_r2k | (flags_r2r << 8)
    return ch, ibuf, state, obuf, flags


def r2hs(s, r2h=r2h):
    """
    convert romaji in the input string to halfwidth katakana. see `r2h()` for a list of supported conversions
    """
    o = ""

    def getch():
        nonlocal s
        ch, s = s[:1], s[1:]
        return ch

    ibuf, state, obuf, flags = "", "", "", 0
    while True:
        ch, ibuf, state, obuf, flags = r2h(
            ibuf=ibuf, state=state, obuf=obuf, flags=flags, getch=getch
        )
        o += ch
        if ch == "":
            break
    return o


def smoketest():
    romaji_specimen = " ".join(
        """
  . [ ] , / wo xa xi xu xe xo xya xyu xyo xtu
  ^ a i u e o ka ki ku ke ko sa si su se so
  ta ti tu te to na ni nu ne no ha hi hu he ho ma
  mi mu me mo ya yu yo ra ri ru re ro wa n' z; z:
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
    compact_romaji_specimen = ".[],/woxaxixuxexoxyaxyuxyoxtu^aiueokakikukekosasisusesotatitutetonaninunenohahihuhehomamimumemoyayuyorarirurerowan'z;z:"
    compact_kana_specimen = (
        "｡｢｣､･ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝﾞﾟ"
    )
    assert compact_romaji_specimen == "".join(romaji_specimen.split(" "))
    assert compact_kana_specimen == "".join(kana_specimen.split(" "))
    assert (
        " ".join(ALL_1_1_STARTS_R)
        == ". [ ] , / wo x xy xtu ^ a i u e o k s t n h m y r wa n' z; z:"
    )
    assert " ".join(expand_1_1_starts(*ALL_1_1_STARTS_R)) == romaji_specimen
    # these tests only require basic 1:1 romaji-to-kana translation, without rewriting
    for r2k_one_to_one_impl in (
        r2k_one_to_one_simple,
        r2k_one_to_one_fast,
        r2k_one_to_one,
        r2h,
    ):
        r2ks = lambda s: r2hs(s, r2h=r2k_one_to_one_impl)
        assert r2ks("") == ""
        assert (
            " ".join([r2ks(romaji) for romaji in expand_1_1_starts(*ALL_1_1_STARTS_R)])
            == kana_specimen
        )
        assert set(
            r2ks(ch) == ALL_K[i]
            for i, ch in enumerate(expand_1_1_starts(*ALL_1_1_STARTS_R))
        ) == {True}
        assert (
            r2ks(romaji_specimen) == kana_specimen
        ), f"r2ks({repr(romaji_specimen)}) failed, expected: \n {repr(kana_specimen)}, but got:\n {repr(r2ks(romaji_specimen))}"
        assert (
            r2ks(compact_romaji_specimen) == compact_kana_specimen
        ), f"r2ks({repr(compact_romaji_specimen)}) failed, expected: \n {repr(compact_kana_specimen)}, but got:\n {repr(r2ks(compact_romaji_specimen))}"
        assert r2ks(compact_romaji_specimen) == bytes(
            range(0xA1, 1 + 0xDF)
        ).decode(  # single-byte kana portion of Shift JIS
            "cp932"
        )
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
        assert r2ks("tixyokore-to") == "ﾁｮｺﾚｰﾄ"
        assert r2ks("Ra-men'") == "ﾗｰﾒﾝ"
        assert r2ks("KIXYAN'TO/HAZ;I/MI-/RAHUZ;") == "ｷｬﾝﾄ･ﾊﾞｲ･ﾐｰ･ﾗﾌﾞ"
        assert r2ks("hiz;xyu-texihuru/san'tez;-") == "ﾋﾞｭｰﾃｨﾌﾙ･ｻﾝﾃﾞｰ"
        assert r2ks("Haz;rakuZ/Ohaz;ma") == "ﾊﾞﾗｸ･ｵﾊﾞﾏ"
        assert r2ks("Haz:-sonaru/Kon'hiz:xyu-ta-") == "ﾊﾟｰｿﾅﾙ･ｺﾝﾋﾟｭｰﾀｰ"
        assert r2ks("Taz;/Uz;xin'ti=Taz;Uz;xin'ti") == "ﾀﾞ･ｳﾞｨﾝﾁ=ﾀﾞｳﾞｨﾝﾁ"
        assert r2ks("UZ;XARISU") == "ｳﾞｧﾘｽ"
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
        assert r2ks("kixya") == "ｷｬ"
        assert r2ks("kixyu") == "ｷｭ"
        assert r2ks("ya") == "ﾔ"
        assert r2ks("ki\b") == "ｷ\b"
        assert r2ks("kixya\b") == "ｷｬ\b"
        assert r2ks("kixyu\b") == "ｷｭ\b"
        assert r2ks("ya\b") == "ﾔ\b"
        assert r2ks("\bki") == "\bｷ"
        assert r2ks("\bkixya") == "\bｷｬ"
        assert r2ks("\bkixyu") == "\bｷｭ"
        assert r2ks("\bya") == "\bﾔ"
        assert r2ks("\bki\b") == "\bｷ\b"
        assert r2ks("\bkixya\b") == "\bｷｬ\b"
        assert r2ks("\bkixyu\b") == "\bｷｭ\b"
        assert r2ks("\bya\b") == "\bﾔ\b"
        assert r2ks("k\bi") == "ｲ"
        assert r2ks("k\bya") == "ﾔ"
        assert r2ks("kixy\ba") == "ｷｧ"
        assert r2ks("k\byu") == "ﾕ"
        assert r2ks("kixy\bu") == "ｷｩ"
        assert r2ks("kixy\bya") == "ｷｬ"
        assert r2ks("kixy\byu") == "ｷｭ"
        assert r2ks("kixy\b\ba") == "ｷｱ"
        assert r2ks("kixy\b\bu") == "ｷｳ"
        assert r2ks("kixy\b\bya") == "ｷﾔ"
        assert r2ks("kixy\b\byu") == "ｷﾕ"
        assert r2ks("ﾌ-") == "ﾌｰ"
        assert r2ks("hu-") == "ﾌｰ"
        assert r2ks("h\b-") == "-"
        assert r2ks("h\b-") == "-"
        assert r2ks("hux\bu") == "ﾌｳ"
        assert r2ks("hux\bu") == "ﾌｳ"
        assert r2ks("h\bhuxyahux\byuhuxy\byohux\b\bhuxy\b\b-") == "ﾌｬﾌﾕﾌｮﾌ\bﾌｰ"
        assert r2ks("ku") == "ｸ"
        assert r2ks("k\bu") == "ｳ"
        assert r2ks("kuxu") == "ｸｩ"
        assert r2ks("kux\bu") == "ｸｳ"
        assert r2ks("kon'nitiha") == "ｺﾝﾆﾁﾊ"
        assert r2ks("aaiiuueeoo") == "ｱｱｲｲｳｳｴｴｵｵ"
        assert r2ks("a-i-u-e-o-") == "ｱｰｲｰｳｰｴｰｵｰ"
        assert r2ks("xtuuxaxtuuxixtuuxtuuxextuuxo") == "ｯｳｧｯｳｨｯｳｯｳｪｯｳｫ"
        assert r2ks("xtuuz;xaxtuuz;xixtuuz;xtuuz;xextuuz;xo") == "ｯｳﾞｧｯｳﾞｨｯｳﾞｯｳﾞｪｯｳﾞｫ"
        assert r2ks("xtutixyaxtutixixtutixyuxtutixextutixyo") == "ｯﾁｬｯﾁｨｯﾁｭｯﾁｪｯﾁｮ"
        assert r2ks("xtuhuxaxtuhuxixtuhuxtuhuxextuhuxo") == "ｯﾌｧｯﾌｨｯﾌｯﾌｪｯﾌｫ"
        assert r2ks("xtuhaz;xtuhiz;xtuhuz;xtuhez;xtuhoz;") == "ｯﾊﾞｯﾋﾞｯﾌﾞｯﾍﾞｯﾎﾞ"
        assert (
            r2ks("xtuhuz:xaxtuhuz:xixtuhuz:xuxtuhuz:xextuhuz:xo")
            == "ｯﾌﾟｧｯﾌﾟｨｯﾌﾟｩｯﾌﾟｪｯﾌﾟｫ"
        )
        assert (
            r2ks("xtuhiz;xyaxtuhiz;xixtuhiz;xyuxtuhiz;xextuhiz;xyo")
            == "ｯﾋﾞｬｯﾋﾞｨｯﾋﾞｭｯﾋﾞｪｯﾋﾞｮ"
        )
        assert (
            r2ks("xtuhiz:xyaxtuhiz:xixtuhiz:xyuxtuhiz:xextuhiz:xyo")
            == "ｯﾋﾟｬｯﾋﾟｨｯﾋﾟｭｯﾋﾟｪｯﾋﾟｮ"
        )
        assert (
            r2ks("xtuhuz:xaxtuhuz:xixtuhuz:xuxtuhuz:xextuhuz:xo")
            == "ｯﾌﾟｧｯﾌﾟｨｯﾌﾟｩｯﾌﾟｪｯﾌﾟｫ"
        )
        assert r2ks("xtuyaxtuixtuyuxtuixextuyo") == "ｯﾔｯｲｯﾕｯｲｪｯﾖ"
        assert r2ks("yaaiiyuuixeeyoo") == "ﾔｱｲｲﾕｳｲｪｴﾖｵ"
        assert r2ks("ya-i-yu-ixe-yo-") == "ﾔｰｲｰﾕｰｲｪｰﾖｰ"
        assert (
            r2ks(
                """
                    huxa    huxi       hu    huxe     huxo
                   huxya            huxyu            huxyo
                    huxa    huxi     huxu    huxe     huxo
                 xtuhuxa xtuhuxi    xtuhu xtuhuxe  xtuhuxo
                xtuhuxya         xtuhuxyu         xtuhuxyo
                 xtuhuxa xtuhuxi  xtuhuxu xtuhuxe  xtuhuxo
                """
            ).split()
            == """
             ﾌｧ   ﾌｨ   ﾌ   ﾌｪ   ﾌｫ
             ﾌｬ        ﾌｭ       ﾌｮ
             ﾌｧ   ﾌｨ   ﾌｩ  ﾌｪ   ﾌｫ
            ｯﾌｧ  ｯﾌｨ  ｯﾌ  ｯﾌｪ  ｯﾌｫ
            ｯﾌｬ       ｯﾌｭ      ｯﾌｮ
            ｯﾌｧ  ｯﾌｨ  ｯﾌｩ ｯﾌｪ  ｯﾌｫ
            """.split()
        )
        assert (
            r2ks(
                """
                    uz;xa    uz;xi        uz;    uz;xe     uz;xo
                   uz;xya    uz;xi     uz;xyu    uz;xe    uz;xyo
                 xtuuz;xa xtuuz;xi     xtuuz; xtuuz;xe  xtuuz;xo
                xtuuz;xya xtuuz;xi  xtuuz;xyu xtuuz;xe xtuuz;xyo
                """
            ).split()
            == """
             ｳﾞｧ  ｳﾞｨ  ｳﾞ   ｳﾞｪ  ｳﾞｫ
             ｳﾞｬ  ｳﾞｨ  ｳﾞｭ  ｳﾞｪ  ｳﾞｮ
            ｯｳﾞｧ ｯｳﾞｨ ｯｳﾞ  ｯｳﾞｪ ｯｳﾞｫ
            ｯｳﾞｬ ｯｳﾞｨ ｯｳﾞｭ ｯｳﾞｪ ｯｳﾞｮ
            """.split()
        )
        assert (
            r2ks("nanixyanan'yanan'nixyan'n'n'n'xtun'xtun'n'n'n'n'~")
            == "ﾅﾆｬﾅﾝﾔﾅﾝﾆｬﾝﾝﾝﾝｯﾝｯﾝﾝﾝﾝﾝ~"
        )
    # tests from here onward may require romaji-to-romaji rewriting
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
        ___dzadzidzudzedzo="ﾂﾞｧﾂﾞｨﾂﾞﾂﾞｪﾂﾞｫ",
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

           n        a-
          n'         ^
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
      dza  dzi  dzu  dze  dzo
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

            ﾝ           ｱｰ
            ﾝ           ｰ
            ﾝ          ｯｶ
            ﾝ          ｯｧ
            ﾝ          ｯｧ

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
    ﾂﾞｧ ﾂﾞｨ ﾂﾞ  ﾂﾞｪ ﾂﾞｫ
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
        r2hs(long_romaji_specimen).split() == long_kana_specimen.split()
    ), f"r2hs({repr(long_romaji_specimen)}) failed, expected: \n {repr(long_kana_specimen)}, but got:\n {repr(r2hs(long_romaji_specimen))}"
    assert r2hs("Ra-men") == "ﾗｰﾒﾝ"
    assert r2hs("cyocore-to") == "ﾁｮｺﾚｰﾄ"
    assert r2hs("chokore-to") == "ﾁｮｺﾚｰﾄ"
    assert r2hs("tyokore-to") == "ﾁｮｺﾚｰﾄ"
    assert r2hs("chilyokore-to") == "ﾁｮｺﾚｰﾄ"
    assert r2hs("KYANTO/BAI/MI-/RABU") == "ｷｬﾝﾄ･ﾊﾞｲ･ﾐｰ･ﾗﾌﾞ"
    assert r2hs("byu-t'ifuru/sande-") == "ﾋﾞｭｰﾃｨﾌﾙ･ｻﾝﾃﾞｰ"
    assert r2hs("BarakuZ/Obama") == "ﾊﾞﾗｸ･ｵﾊﾞﾏ"
    assert r2hs("Pa-sonaru/Conpyu-ta-") == "ﾊﾟｰｿﾅﾙ･ｺﾝﾋﾟｭｰﾀｰ"
    assert r2hs("Da/Vinchi=DaVinchi") == "ﾀﾞ･ｳﾞｨﾝﾁ=ﾀﾞｳﾞｨﾝﾁ"
    assert r2hs("VARISU") == "ｳﾞｧﾘｽ"
    assert r2hs("I-SU") == "ｲｰｽ"
    assert r2hs("I^su") == "ｲｰｽ"
    assert r2hs("a-123") == "ｱｰ123"
    assert r2hs("az-123") == "ｱ-123"
    assert r2hs("\b") == "\b"
    assert r2hs("\x7f") == "\x7f"
    assert r2hs("a\b-") == "ｱ\b-"
    assert r2hs("a\x7f-") == "ｱ\x7f-"
    assert r2hs("a -") == "ｱ -"
    assert r2hs("a \b-") == "ｱ \bｰ"
    assert r2hs("a \x7f-") == "ｱ \x7fｰ"
    assert r2hs("a\n\b-") == "ｱ\n\b-"
    assert r2hs("a\r\x7f-") == "ｱ\r\x7f-"
    assert r2hs("k\ba\b-") == "ｱ\b-"
    assert r2hs("k\ba\x7f-") == "ｱ\x7f-"
    assert r2hs("k\ba -") == "ｱ -"
    assert r2hs("k\ba \b-") == "ｱ \bｰ"
    assert r2hs("k\ba \x7f-") == "ｱ \x7fｰ"
    assert r2hs("ak\b\b-") == "ｱ\b-"
    assert r2hs("ak\x7fk\x7f-") == "ｱｰ"
    assert r2hs("a k\b-") == "ｱ -"
    assert r2hs("a k\b\b-") == "ｱ \bｰ"
    assert r2hs("a k\x7f\x7f-") == "ｱ \x7fｰ"
    assert r2hs("k\ba\bk\b-") == "ｱ\b-"
    assert r2hs("k\ba\x7fk\x7f-") == "ｱ\x7f-"
    assert r2hs("k\ba k\b-") == "ｱ -"
    assert r2hs("k\ba \bk\b-") == "ｱ \bｰ"
    assert r2hs("k\ba \x7fk\x7f-") == "ｱ \x7fｰ"
    assert r2hs("ki") == "ｷ"
    assert r2hs("kya") == "ｷｬ"
    assert r2hs("kyu") == "ｷｭ"
    assert r2hs("ya") == "ﾔ"
    assert r2hs("ki\b") == "ｷ\b"
    assert r2hs("kya\b") == "ｷｬ\b"
    assert r2hs("kyu\b") == "ｷｭ\b"
    assert r2hs("ya\b") == "ﾔ\b"
    assert r2hs("\bki") == "\bｷ"
    assert r2hs("\bkya") == "\bｷｬ"
    assert r2hs("\bkyu") == "\bｷｭ"
    assert r2hs("\bya") == "\bﾔ"
    assert r2hs("\bki\b") == "\bｷ\b"
    assert r2hs("\bkya\b") == "\bｷｬ\b"
    assert r2hs("\bkyu\b") == "\bｷｭ\b"
    assert r2hs("\bya\b") == "\bﾔ\b"
    assert r2hs("k\bi") == "ｲ"
    assert r2hs("k\bya") == "ﾔ"
    assert r2hs("ky\ba") == "ｶ"
    assert r2hs("k\byu") == "ﾕ"
    assert r2hs("ky\bu") == "ｸ"
    assert r2hs("ky\bya") == "ｷｬ"
    assert r2hs("ky\byu") == "ｷｭ"
    assert r2hs("ky\b\ba") == "ｱ"
    assert r2hs("ky\b\bu") == "ｳ"
    assert r2hs("ky\b\bya") == "ﾔ"
    assert r2hs("ky\b\byu") == "ﾕ"
    assert r2hs("ﾌ-") == "ﾌｰ"
    assert r2hs("fu-") == "ﾌｰ"
    assert r2hs("f\b-") == "-"
    assert r2hs("f\b-") == "-"
    assert r2hs("fw\bu") == "ﾌ"
    assert r2hs("fw\bwu") == "ﾌｩ"
    assert r2hs("f\bfyafw\byufy\byofw\b\bfy\b\b-") == "ﾌｬﾌｭﾌｮｰ"
    assert r2hs("qu") == "ｸ"
    assert r2hs("q\bu") == "ｳ"
    assert r2hs("kwu") == "ｸｩ"
    assert r2hs("kw\bu") == "ｸ"
    assert r2hs("konnnichiha") == "ｺﾝﾆﾁﾊ"
    assert r2hs("kon'nichiha") == "ｺﾝﾆﾁﾊ"
    assert r2hs("kon'nitiha") == "ｺﾝﾆﾁﾊ"
    assert r2hs("colnnitiha") == "ｺﾝﾆﾁﾊ"
    assert r2hs("coxnnitiha") == "ｺﾝﾆﾁﾊ"
    assert r2hs("aaiiuueeoo") == "ｱｱｲｲｳｳｴｴｵｵ"
    assert r2hs("a-i-u-e-o-") == "ｱｰｲｰｳｰｴｰｵｰ"
    assert r2hs("wwhawwhiwwhuwwhewwho") == "ｯｳｧｯｳｨｯｳｯｳｪｯｳｫ"
    assert r2hs("vvavvivvuvvevvo") == "ｯｳﾞｧｯｳﾞｨｯｳﾞｯｳﾞｪｯｳﾞｫ"
    assert r2hs("ttyattyittyuttyettyo") == "ｯﾁｬｯﾁｨｯﾁｭｯﾁｪｯﾁｮ"
    assert r2hs("ccyaccyiccyuccyeccyo") == "ｯﾁｬｯﾁｨｯﾁｭｯﾁｪｯﾁｮ"
    assert r2hs("ffaffiffuffeffo") == "ｯﾌｧｯﾌｨｯﾌｯﾌｪｯﾌｫ"
    assert r2hs("bbabbibbubbebbo") == "ｯﾊﾞｯﾋﾞｯﾌﾞｯﾍﾞｯﾎﾞ"
    assert r2hs("pphapphipphuppheppho") == "ｯﾌﾟｧｯﾌﾟｨｯﾌﾟｩｯﾌﾟｪｯﾌﾟｫ"
    assert r2hs("bbyabbyibbyubbyebbyo") == "ｯﾋﾞｬｯﾋﾞｨｯﾋﾞｭｯﾋﾞｪｯﾋﾞｮ"
    assert r2hs("ppyappyippyuppyeppyo") == "ｯﾋﾟｬｯﾋﾟｨｯﾋﾟｭｯﾋﾟｪｯﾋﾟｮ"
    assert r2hs("pphapphipphuppheppho") == "ｯﾌﾟｧｯﾌﾟｨｯﾌﾟｩｯﾌﾟｪｯﾌﾟｫ"
    assert r2hs("yyayyiyyuyyeyyo") == "ｯﾔｯｲｯﾕｯｲｪｯﾖ"
    assert r2hs("yaayiiyuuyeeyoo") == "ﾔｱｲｲﾕｳｲｪｴﾖｵ"
    assert r2hs("ya-yi-yu-ye-yo-") == "ﾔｰｲｰﾕｰｲｪｰﾖｰ"
    assert (
        r2hs(
            """
      fa   fi   fu   fe   fo     fya       fyu       fyo     fwa  fwi  fwu  fwe  fwo
     ffa  ffi  ffu  ffe  ffo    ffya      ffyu      ffyo    ffwa ffwi ffwu ffwe ffwo
    """
        ).split()
        == """
      ﾌｧ   ﾌｨ   ﾌ   ﾌｪ   ﾌｫ      ﾌｬ        ﾌｭ        ﾌｮ      ﾌｧ   ﾌｨ   ﾌｩ   ﾌｪ   ﾌｫ
     ｯﾌｧ  ｯﾌｨ  ｯﾌ  ｯﾌｪ  ｯﾌｫ     ｯﾌｬ       ｯﾌｭ       ｯﾌｮ     ｯﾌｧ  ｯﾌｨ  ｯﾌｩ  ｯﾌｪ  ｯﾌｫ
    """.split()
    )
    assert (
        r2hs(
            """
      va   vi   vu   ve   vo     vya  vyi  vyu  vye  vyo
     vva  vvi  vvu  vve  vvo    vvya vvyi vvyu vvye vvyo
    """
        ).split()
        == """
     ｳﾞｧ  ｳﾞｨ  ｳﾞ   ｳﾞｪ  ｳﾞｫ     ｳﾞｬ  ｳﾞｨ  ｳﾞｭ  ｳﾞｪ  ｳﾞｮ
    ｯｳﾞｧ ｯｳﾞｨ ｯｳﾞ  ｯｳﾞｪ ｯｳﾞｫ    ｯｳﾞｬ ｯｳﾞｨ ｯｳﾞｭ ｯｳﾞｪ ｯｳﾞｮ
    """.split()
    )
    assert r2hs("nanyanannyanannnyan'nxnlnxxnllnxnnlnn~") == "ﾅﾆｬﾅﾝﾔﾅﾝﾆｬﾝﾝﾝﾝｯﾝｯﾝﾝﾝﾝﾝ~"

    # some error handling tests
    assert r2hs("abcdefghijklmnopqrstuvwxyz") == "ｱbcﾃﾞfgﾋjklmﾉpqrsﾂvwxyz"
    assert (
        r2hs("a b c d e f g h i j k l m n o p q r s t u v w x y z")
        == "ｱ b c d ｴ f g h ｲ j k l m ﾝ ｵ p q r s t ｳ v w x y z"
    )
    assert (
        r2hs("aabbccddeeffgghhiijjkkllmmnnooppqqrrssttuuvvwwxxyyzz")
        == "ｱｱｯbｯcｯﾃﾞｴｯfｯgｯﾋｲｯjｯkｯlｯmﾝｵｵｯpｯqｯrｯsｯﾂｳｯvｯwｯxｯyｯz"
    )
    assert (
        r2hs(
            "aa bb cc dd ee ff gg hh ii jj kk ll mm nn oo pp qq rr ss tt uu vv ww xx yy zz"
        )
        == "ｱｱ ｯb ｯc ｯd ｴｴ ｯf ｯg ｯh ｲｲ ｯj ｯk ｯl ｯm ﾝ ｵｵ ｯp ｯq ｯr ｯs ｯt ｳｳ ｯv ｯw ｯx ｯy ｯz"
    )

    for cc in range(128):
        ch = chr(cc)
        if ch.lower() in PUNCT_A:
            assert (
                r2hs(ch) == PUNCT_K[PUNCT_A.index(ch.lower())]
            ), f"conversion failed for punctuation {ch}: got {r2hs(ch)}"
        elif ch.lower() in AIUEO_R_SET:
            assert (
                r2hs(ch) == AIUEO_K[AIUEO_R.index(ch.lower())]
            ), f"conversion failed for vowel {ch}: got {r2hs(ch)}"
        elif ch.lower() == "n":
            assert (
                r2hs(ch) == NN_K
            ), f"conversion failed for moraic {ch}: got {r2hs(ch)}"
        elif ch.lower() == CHOUONPU_A:
            assert (
                r2hs(ch) == CHOUONPU_K
            ), f"conversion failed for chouonpu {ch}: got {r2hs(ch)}"
        else:
            assert r2hs(ch) == ch, f"conversion failed for {ch}: got {r2hs(ch)}"


smoketest()

import sys
import unicodedata


def main():
    """
    When invoked with no arguments, this acts as a filter from stdin to stdout.
    When invoked with arguments, each is treated as a filename and filtered to stdout.
    The special filename `-` refers to stdin.
    """
    ibuf, state, obuf, flags = "", "", "", 0
    _, *filenames = sys.argv
    filenames = filenames or ["-"]
    for filename in filenames:
        with sys.stdin if filename == "-" else open(filename, "r") as source:
            while True:
                ch, ibuf, state, obuf, flags = r2h(
                    ibuf=ibuf,
                    state=state,
                    obuf=obuf,
                    flags=flags,
                    getch=lambda: source.read(1),
                )
                if ch == "":
                    break
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
