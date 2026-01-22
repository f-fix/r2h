# About
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

## Usage:
```bash
python3 r2h.py [ FILENAMES... ]
```
When invoked with no arguments, this acts as a filter from stdin to stdout.
When invoked with arguments, each is treated as a filename and filtered to stdout.
The special filename `-` refers to stdin.

## Example input and output
Basic inputs that output a single character each:
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
       wa          wo        ﾜ     ｳ     ｦ
      xya   xyu   xyo        ｬ     ｭ     ｮ     (small versions of ya/yu/yo)
       xa xi xu xe xo        ｧ  ｨ  ｩ  ｪ  ｫ     (small versions of a/i/u/e/o)
            xtu                    ｯ           (small tsu)
       n'                    ﾝ                 (moraic n)

       ^                     ｰ                 (chouonpu)
       -                     ｰ or -            (contextual: chouonpu after kana, hyphen-minus elsewhere)
       z;                    ﾞ                 (dakuten)
       z:                    ﾟ                 (handakuten)
       z-                    -                 (hyphen-minus)
       z/ or /               ･                 (middle dot)
       .                     ｡                 (ideographic full stop)
       ,                     ､                 (ideographic comma)
       [                     ｢                 (left corner bracket)
       ]                     ｣                 (right corner bracket)
```
all supported inputs:
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
       n' or nn or xn or ln or n          ﾝ                 (moraic n)
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
How that should look in hiragana: (except it will be halfwidth, which Unicode cannot do)
```
     a  i  u  e  o  ya  yi  yu  ye  yo    あ  い  う  え  お や   い   ゆ  いぇ よ
    ka ki ku ke ko kya kyi kyu kye kyo    か  き  く  け  こ きゃ きぃ きゅ きぇ きょ
    sa si su se so sya syi syu sye syo    さ  し  す  せ  そ しゃ しぃ しゅ しぇ しょ
    ta ti tu te to tya tyi tyu tye tyo    た  ち  つ  て  と ちゃ ちぃ ちゅ ちぇ ちょ
    na ni nu ne no nya nyi nyu nye nyo    な  に  ぬ  ね  の にゃ にぃ にゅ にぇ にょ
    ha hi hu he ho hya hyi hyu hye hyo    は  ひ  ふ  へ  ほ ひゃ ひぃ ひゅ ひぇ ひょ
    ma mi mu me mo mya myi myu mye myo    ま  み  む  め  も みゃ みぃ みゅ みぇ みょ
    ra ri ru re ro rya ryi ryu rye ryo    ら  り  る  れ  ろ りゃ りぃ りゅ りぇ りょ
    wa wi wu we wo                        わ  うぃ う  うぇ を

    ga gi gu ge go gya gyi gyu gye gyo    が ぎ ぐ げ ご ぎゃ ぎぃ ぎゅ ぎぇ ぎょ
    za zi zu ze zo zya zyi zyu zye zyo    ざ じ ず ぜ ぞ じゃ じぃ じゅ じぇ じょ
    da di du de do dya dyi dyu dye dyo    だ ぢ づ で ど ぢゃ ぢぃ ぢゅ ぢぇ ぢょ
    ba bi bu be bo bya byi byu bye byo    ば び ぶ べ ぼ びゃ びぃ びゅ びぇ びょ
    pa pi pu pe po pya pyi pyu pye pyo    ぱ ぴ ぷ ぺ ぽ ぴゃ ぴぃ ぴゅ ぴぇ ぴょ

      wha  whi  whu  whe  who             うぁ うぃ う  うぇ うぉ
      kwa  kwi  kwu  kwe  kwo             くぁ くぃ くぅ くぇ くぉ
       qa   qi   qu   qe   qo             くぁ くぃ く  くぇ くぉ
      qya       qyu       qyo             くゃ      くゅ    くょ
      qwa  qwi  qwu  qwe  qwo             くぁ くぃ くぅ くぇ くぉ
      cwa  cwi  cwu  cwe  cwo             くぁ くぃ くぅ くぇ くぉ
       ca   ci   cu   ce   co             か   し   く   せ   こ
      cya  cyi  cyu  cye  cyo             ちゃ ちぃ ちゅ ちぇ ちょ
      sha  shi  shu  she  sho             しゃ し  しゅ しぇ しょ
      swa  swi  swu  swe  swo             すぁ すぃ すぅ すぇ すぉ
      cha  chi  chu  che  cho             ちゃ ち  ちゅ ちぇ ちょ
      tsa  tsi  tsu  tse  tso             つぁ つぃ つ  つぇ つぉ
      tha  thi  thu  the  tho             てゃ てぃ てゅ てぇ てょ
      twa  twi  twu  twe  two             とぁ とぃ とぅ とぇ とぉ
           t'i  t'u                           てぃ とぅ
                t'yu                              てゅ
       fa   fi   fu   fe   fo             ふぁ ふぃ ふ  ふぇ ふぉ
      fya       fyu       fyo             ふゃ    ふゅ    ふょ
      hwa  hwi       hwe  hwo             ふぁ ふぃ    ふぇ ふぉ
               hwyu                               ふゅ
      fwa  fwi  fwu  fwe  fwo             ふぁ ふぃ ふぅ ふぇ ふぉ

       va   vi   vu   ve   vo             ゔぁ ゔぃ ゔ ゔぇ ゔぉ
      vya  vyi  vyu  vye  vyo             ゔゃ ゔぃ ゔゅ ゔぇ ゔょ
      gwa  gwi  gwu  gwe  gwo             ぐぁ ぐぃ ぐぅ ぐぇ ぐぉ
       ja   ji   ju   je   jo             じゃ じ じゅ じぇ じょ
      jya  jyi  jyu  jye  jyo             じゃ じぃ じゅ じぇ じょ
      zwa  zwi  zwu  zwe  zwo             ずぁ ずぃ ずぅ ずぇ ずぉ
      dza  dzi  dzu  dze  dzo             づぁ づぃ づ づぇ づぉ
      dha  dhi  dhu  dhe  dho             でゃ でぃ でゅ でぇ でょ
      dwa  dwi  dwu  dwe  dwo             どぁ どぃ どぅ どぇ どぉ
           d'i  d'u                           でぃ どぅ
               d'yu                               でゅ
      pha  phi  phu  phe  pho             ぷぁ ぷぃ ぷぅ ぷぇ ぷぉ

       xa   xi   xu   xe   xo             ぁ  ぃ  ぅ  ぇ  ぉ (small versions of a/i/u/e/o)
      xya  xyi  xyu  xye  xyo             ゃ  ぃ  ゅ  ぇ  ょ (small versions of ya/i/yu/e/yo)
                xtu                               っ        (small tsu)
               xtsu                               っ        (small tsu)
       la   li   lu   le   lo             ぁ  ぃ  ぅ  ぇ  ぉ (small versions of a/i/u/e/o)
      lya  lyi  lyu  lye  lyo             ゃ  ぃ  ゅ  ぇ  ょ (small versions of ya/i/yu/e/yo)
                ltu                               っ        (small tsu)
               ltsu                               っ        (small tsu)
       (repeated consonant other than n)          っ        (small tsu for all but the final instance)
       n' or nn or xn or ln or n          ん                (moraic n)
       ^                                  ー                (chouonpu)
       -                                  ー or -            (contextual: chouonpu after kana, hyphen-minus elsewhere)
       z;                                ゛                (dakuten)
       z:                                ゜                (handakuten)
       z-                                 -                 (hyphen-minus)
       z/ or /                            ・                (middle dot)
       .                                  ｡                (ideographic full stop)
       ,                                  ､                (ideographic comma)
       [                                  ｢                (left corner bracket)
       ]                                  ｣                (right corner bracket)
```
