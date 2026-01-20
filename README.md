# About
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

## Usage:
```bash
python3 r2h.py [ FILENAMES... ]
```
When invoked with no arguments, this acts as a filter from stdin to stdout.
When invoked with arguments, each is treated as a filename and filtered to stdout.
The special filename `-` refers to stdin.

## Example input and output
Input:
```
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
```
Output: (spacing/indentation has been adjusted)
```
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
```
here's approximately how that should look in hiragana:  (except halfwidth)
```
    あ   い   う   え   お   や   い   ゆ   いぇ  よ
    か   き   く   け   こ   きゃ  きぃ  きゅ  きぇ  きょ
    さ   し   す   せ   そ   しゃ  しぃ  しゅ  しぇ  しょ
    た   ち   つ   て   と   ちゃ  ちぃ  ちゅ  ちぇ  ちょ
    な   に   ぬ   ね   の   にゃ  にぃ  にゅ  にぇ  にょ
    は   ひ   ふ   へ   ほ   ひゃ  ひぃ  ひゅ  ひぇ  ひょ
    ま   み   む   め   も   みゃ  みぃ  みゅ  みぇ  みょ
    ら   り   る   れ   ろ   りゃ  りぃ  りゅ  りぇ  りょ
    わ   うぃ  う   うぇ  を

    が  ぎ  ぐ  げ  ご  ぎゃ ぎぃ ぎゅ ぎぇ ぎょ
    ざ  じ  ず  ぜ  ぞ  じゃ じぃ じゅ じぇ じょ
    だ  ぢ  づ  で  ど  ぢゃ ぢぃ ぢゅ ぢぇ ぢょ
    ば  び  ぶ  べ  ぼ  びゃ びぃ びゅ びぇ びょ
    ぱ  ぴ  ぷ  ぺ  ぽ  ぴゃ ぴぃ ぴゅ ぴぇ ぴょ

      ん      あｰ
      ん      ｰ
      ん      っか
      ん      っぁ

    うぁ  うぃ  う   うぇ  うぉ
    くぁ  くぃ  くぅ  くぇ  くぉ
    くぁ  くぃ  く   くぇ  くぉ  くゃ      くゅ      くょ
    くぁ  くぃ  くぅ  くぇ  くぉ
    くぁ  くぃ  くぅ  くぇ  くぉ
    か   し   く   せ   こ   ちゃ  ちぃ  ちゅ  ちぇ  ちょ
    しゃ  し   しゅ  しぇ  しょ
    すぁ  すぃ  すぅ  すぇ  すぉ
    ちゃ  ち   ちゅ  ちぇ  ちょ
    つぁ  つぃ  つ   つぇ  つぉ
    てゃ  てぃ  てゅ  てぇ  てょ
    とぁ  とぃ  とぅ  とぇ  とぉ
        てぃ  とぅ                  てゅ
    ふぁ  ふぃ  ふ   ふぇ  ふぉ  ふゃ      ふゅ      ふょ
    ふぁ  ふぃ      ふぇ  ふぉ          ふゅ
    ふぁ  ふぃ  ふぅ  ふぇ  ふぉ

    ゔぁ ゔぃ ゔ  ゔぇ ゔぉ ゔゃ ゔぃ ゔゅ ゔぇ ゔょ
    ぐぁ ぐぃ ぐぅ ぐぇ ぐぉ
    じゃ  じ じゅ じぇ じょ じゃ じぃ じゅ じぇ じょ
    ずぁ ずぃ ずぅ ずぇ ずぉ
    でゃ でぃ でゅ でぇ でょ
    どぁ どぃ どぅ どぇ どぉ
        でぃ どぅ                 でゅ
    ぷぁ ぷぃ ぷぅ ぷぇ ぷぉ

    ぁ   ぃ   ぅ   ぇ   ぉ   ゃ  ぃ  ゅ  ぇ  ょ
            っ
            っ
    ぁ   ぃ   ぅ   ぇ   ぉ   ゃ  ぃ  ゅ  ぇ  ょ
            っ
            っ
```
