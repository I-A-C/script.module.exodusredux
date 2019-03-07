"""
    resolveurl XBMC Addon
    Copyright (C) 2013 Bstrdsmkr

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Adapted for use in xbmc from:
    https://github.com/einars/js-beautify/blob/master/python/jsbeautifier/unpackers/packer.py

    usage:

    if detect(some_string):
        unpacked = unpack(some_string)


Unpacker for Dean Edward's p.a.c.k.e.r
"""

import re


def detect(source):
    """Detects whether `source` is P.A.C.K.E.R. coded."""
    source = source.replace(' ', '')
    if re.search('eval\(function\(p,a,c,k,e,(?:r|d)', source):
        return True
    else:
        return False


def unpack(source):
    """Unpacks P.A.C.K.E.R. packed js code."""
    payload, symtab, radix, count = _filterargs(source)

    if count != len(symtab):
        raise UnpackingError('Malformed p.a.c.k.e.r. symtab.')

    try:
        unbase = Unbaser(radix)
    except TypeError:
        raise UnpackingError('Unknown p.a.c.k.e.r. encoding.')

    def lookup(match):
        """Look up symbols in the synthetic symtab."""
        word = match.group(0)
        return symtab[unbase(word)] or word

    source = re.sub(r'\b\w+\b', lookup, payload)
    return _replacestrings(source)


def _filterargs(source):
    """Juice from a source file the four args needed by decoder."""
    argsregex = (r"}\s*\('(.*)',\s*(.*?),\s*(\d+),\s*'(.*?)'\.split\('\|'\)")
    args = re.search(argsregex, source, re.DOTALL).groups()

    try:
        payload, radix, count, symtab = args
        radix = 36 if not radix.isdigit() else int(radix)
        return payload, symtab.split('|'), radix, int(count)
    except ValueError:
        raise UnpackingError('Corrupted p.a.c.k.e.r. data.')


def _replacestrings(source):
    """Strip string lookup table (list) and replace values in source."""
    match = re.search(r'var *(_\w+)\=\["(.*?)"\];', source, re.DOTALL)

    if match:
        varname, strings = match.groups()
        startpoint = len(match.group(0))
        lookup = strings.split('","')
        variable = '%s[%%d]' % varname
        for index, value in enumerate(lookup):
            source = source.replace(variable % index, '"%s"' % value)
        return source[startpoint:]
    return source


class Unbaser(object):
    """Functor for a given base. Will efficiently convert
    strings to natural numbers."""
    ALPHABET = {
        62: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        95: (' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
             '[\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
    }

    def __init__(self, base):
        self.base = base

        # If base can be handled by int() builtin, let it do it for us
        if 2 <= base <= 36:
            self.unbase = lambda string: int(string, base)
        else:
            if base < 62:
                self.ALPHABET[base] = self.ALPHABET[62][0:base]
            elif 62 < base < 95:
                self.ALPHABET[base] = self.ALPHABET[95][0:base]
            # Build conversion dictionary cache
            try:
                self.dictionary = dict((cipher, index) for index, cipher in enumerate(self.ALPHABET[base]))
            except KeyError:
                raise TypeError('Unsupported base encoding.')

            self.unbase = self._dictunbaser

    def __call__(self, string):
        return self.unbase(string)

    def _dictunbaser(self, string):
        """Decodes a  value to an integer."""
        ret = 0
        for index, cipher in enumerate(string[::-1]):
            ret += (self.base ** index) * self.dictionary[cipher]
        return ret


class UnpackingError(Exception):
    """Badly packed source or general error. Argument is a
    meaningful description."""
    pass


if __name__ == "__main__":
    # test = '''eval(function(p,a,c,k,e,d){while(c--)if(k[c])p=p.replace(new RegExp('\\b'+c.toString(a)+'\\b','g'),k[c]);return p}('4(\'30\').2z({2y:\'5://a.8.7/i/z/y/w.2x\',2w:{b:\'2v\',19:\'<p><u><2 d="20" c="#17">2u 19.</2></u><16/><u><2 d="18" c="#15">2t 2s 2r 2q.</2></u></p>\',2p:\'<p><u><2 d="20" c="#17">2o 2n b.</2></u><16/><u><2 d="18" c="#15">2m 2l 2k 2j.</2></u></p>\',},2i:\'2h\',2g:[{14:"11",b:"5://a.8.7/2f/13.12"},{14:"2e",b:"5://a.8.7/2d/13.12"},],2c:"11",2b:[{10:\'2a\',29:\'5://v.8.7/t-m/m.28\'},{10:\'27\'}],26:{\'25-3\':{\'24\':{\'23\':22,\'21\':\'5://a.8.7/i/z/y/\',\'1z\':\'w\',\'1y\':\'1x\'}}},s:\'5://v.8.7/t-m/s/1w.1v\',1u:"1t",1s:"1r",1q:\'1p\',1o:"1n",1m:"1l",1k:\'5\',1j:\'o\',});l e;l k=0;l 6=0;4().1i(9(x){f(6>0)k+=x.r-6;6=x.r;f(q!=0&&k>=q){6=-1;4().1h();4().1g(o);$(\'#1f\').j();$(\'h.g\').j()}});4().1e(9(x){6=-1});4().1d(9(x){n(x)});4().1c(9(){$(\'h.g\').j()});9 n(x){$(\'h.g\').1b();f(e)1a;e=1;}',36,109,'||font||jwplayer|http|p0102895|me|vidto|function|edge3|file|color|size|vvplay|if|video_ad|div||show|tt102895|var|player|doPlay|false||21600|position|skin|test||static|1y7okrqkv4ji||00020|01|type|360p|mp4|video|label|FFFFFF|br|FF0000||deleted|return|hide|onComplete|onPlay|onSeek|play_limit_box|setFullscreen|stop|onTime|dock|provider|391|height|650|width|over|controlbar|5110|duration|uniform|stretching|zip|stormtrooper|213|frequency|prefix||path|true|enabled|preview|timeslidertooltipplugin|plugins|html5|swf|src|flash|modes|hd_default|3bjhohfxpiqwws4phvqtsnolxocychumk274dsnkblz6sfgq6uz6zt77gxia|240p|3bjhohfxpiqwws4phvqtsnolxocychumk274dsnkba36sfgq6uzy3tv2oidq|hd|original|ratio|broken|is|link|Your|such|No|nofile|more|any|availabe|Not|File|OK|previw|jpg|image|setup|flvplayer'.split('|')))'''
    # test = '''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('y.x(A(\'%0%f%b%9%1%d%8%8%o%e%B%c%0%e%d%0%f%w%1%7%3%2%p%d%1%n%2%1%c%0%t%0%f%7%8%8%d%5%6%1%7%e%b%l%7%1%2%e%9%q%c%0%6%1%z%2%0%f%b%1%9%c%0%s%6%6%l%G%4%4%5%5%5%k%b%7%5%8%o%i%2%k%6%i%4%2%3%p%2%n%4%5%7%6%9%s%4%j%q%a%h%a%3%a%E%a%3%D%H%9%K%C%I%m%r%g%h%L%v%g%u%F%r%g%3%J%3%j%3%m%h%4\'));',48,48,'22|72|65|6d|2f|77|74|61|6c|63|4e|73|3d|6f|6e|20|4d|32|76|59|2e|70|51|64|69|62|79|31|68|30|7a|34|66|write|document|75|unescape|67|4f|5a|57|55|3a|44|47|4a|78|49'.split('|'),0,{}))'''
    # test = '''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('x.w(z(\'%1%f%9%b%0%d%7%7%m%e%A%c%1%e%d%1%f%v%0%3%i%2%o%d%0%s%2%0%c%1%q%1%f%3%7%7%d%6%5%0%3%e%9%l%3%0%2%e%b%g%c%1%5%0%y%2%1%f%9%0%b%c%1%r%5%5%l%E%4%4%6%6%6%n%9%3%6%7%m%k%2%n%5%k%4%2%i%o%2%s%4%6%3%5%b%r%4%8%D%h%C%a%F%8%H%B%I%h%i%a%g%8%u%a%q%j%t%j%g%8%t%h%p%j%p%a%G%4\'));',45,45,'72|22|65|61|2f|74|77|6c|5a|73|55|63|3d|6f|6e|20|79|59|6d|4d|76|70|69|2e|62|7a|30|68|64|44|54|66|write|document|75|unescape|67|51|32|6a|3a|35|5f|47|34'.split('|'),0,{}))'''
    # test = '''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('q.r(s(\'%h%t%a%p%u%6%c%n%0%5%l%4%2%4%7%j%0%8%1%o%b%3%7%m%1%8%a%7%b%3%d%6%1%f%0%v%1%5%D%9%0%5%c%g%0%4%A%9%0%f%k%z%2%8%1%C%2%i%d%6%2%3%k%j%2%3%y%e%x%w%g%B%E%F%i%h%e\'));',42,42,'5a|4d|4f|54|6a|44|33|6b|57|7a|56|4e|68|55|3e|47|69|65|6d|32|45|46|31|6f|30|75|document|write|unescape|6e|62|6c|2f|3c|22|79|63|66|78|59|72|61'.split('|'),0,{}))'''
    # test='''eval(function(p,a,c,k,e,d){while(c--)if(k[c])p=p.replace(new RegExp('\\b'+c.toString(a)+'\\b','g'),k[c]);return p}('8("39").38({37:[{p:"4://1.3.2/36/v.35",34:"33"}],32:"4://1.3.2/i/31/30/2z.2y",2x:"2w",2v:"q%",2u:"q%",2t:"16:9",2s:"2r",2q:"2p",2o:[{p:"4://3.2/j?h=2n&g=7",2m:"2l"}],2k:{2j:\'#2i\',2h:14,2g:"2f",2e:0},"2d":{2c:"%2b 2a%o%29%28%27%26.2%25-7.a%22 24%e 23%e 21%e 20%1z 1y%o%1x%22 1w%1v 1u%1t%n%1s%1r%n",1q:"4://3.2/7.a"},1p:"1o",1n:"1m.1l | 1k 1j 1i 1h 1g ",1f:"4://3.2"});1e b,d;8().1d(6(x){k(5>0&&x.1c>=5&&d!=1){d=1;$(\'c.1b\').1a(\'19\')}});8().18(6(x){m(x)});8().17(6(){$(\'c.l\').15()});6 m(x){$(\'c.l\').13();k(b)12;b=1;$.11(\'4://3.2/j?h=10&g=7&z=y-w-u-t-s\',6(f){$(\'#r\').a(f)})}',36,118,'||tv|putload|https||function|3t1tlhv83pqr|jwplayer||html|vvplay|div|vvad|3D0|data|file_code|op||dl|if|video_ad|doPlay|3E|3D|file|100|fviews|2b320c6ae13efa71a060a7076ca296c2|1485454645|106||81||32755|hash|view|get|return|hide||show||onComplete|onPlay|slow|fadeIn|video_ad_fadein|position|onTime|var|aboutlink|Home|Sharing|And|Uploading|Video|TV|PUTLOAD|abouttext|vapor|skin|link|2FIFRAME|3C|3D500|HEIGHT|3D900|WIDTH|22true|allowfullscreen|3DNO|SCROLLING|MARGINHEIGHT||MARGINWIDTH|FRAMEBORDER|2Fembed|2Fputload|2F|3A|22http|SRC|3CIFRAME|code|sharing|backgroundOpacity|Verdana|fontFamily|fontSize|FFFFFF|color|captions|thumbnails|kind|get_slides|tracks|start|startparam|true|androidhls|aspectratio|height|width|4548|duration|jpg|3t1tlhv83pqr_xt|00006|01|image|480|label|mp4|ykgip2nkk62birmpnhxgrirvpya7wwl2t74yvewln767vcte7devr4is3yta|sources|setup|vplayer'.split('|')))'''
    # test='''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('w.C(a(){m(d(\'u\')==e){}},B);a p(4,h,f,6,7){2 3=q r();3.t(3.s()+(f*g*g*o));2 8="; 8="+3.D();k.l=4+"="+h+8+";7="+7+"; 6="+6}a d(4){2 b=4+"=";2 9=k.l.z(\';\');y(2 i=0;i<9.5;i++){2 c=9[i];x(c.A(0)==\' \')c=c.j(1,c.5);m(c.v(b)==0)n c.j(b.5,c.5)}n e}',40,40,'||var|date|name|length|path|domain|expires|ca|function|nameEQ||getcookie|null|hours|60|value||substring|document|cookie|if|return|1000|setcookie|new|Date|getTime|setTime|09ffa5fd853pbe2faac20a3e74138ea72a4807d21f2b|indexOf|window|while|for|split|charAt|5000|setTimeout|toGMTString'.split('|'),0,{}))'''
    # test='''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('j.G=j.w(3(){2(7.c("B-C").k>0){2(7.c("B-C")[0].Y=="X"){j.Z(G);9=7.c("B-C")[0];o=7.c("4").k;n=7.c("v").k;2(o>0){4=7.c("4")[0];4.H=3(){h(4,"e")};4.I=3(){d(4,"e")};9.J(7.F(\'4\'))}7.11.12=3(){2(n>0){d(b,"g")}2(o>0){d(4,"g")}};2(n>0){b=7.c("v")[0];b.H=3(){h(b,"e")};b.I=3(){d(b,"e")};9.J(7.F(\'v\'))}j.w(3(){2(n>0){2(8(9,"f-p")==m){d(b,"g")}l 2(8(9,"f-p")==i&&8(9,"f-E-M")==m&&8(b,"e")==i){h(b,"g")}}2(o>0){j.w(3(){2(8(9,"f-p")==m){d(4,"g")}l 2(8(9,"f-p")==i&&8(9,"f-E-M")==m&&8(4,"e")==i){h(4,"g")}},A)}},A)}}},A);3 8(S,T){y(\' \'+S.5+\' \').Q(\' \'+T+\' \')>-1}3 h(6,5){2(6.q){6.q.14(5)}l 2(!O(6,5)){6.5+=" "+5}}3 d(6,5){2(6.q){6.q.N(5)}l 2(O(6,5)){z P=D V(\'(\\s|^)\'+5+\'(\\s|$)\');6.5=6.5.U(P,\' \')}}W.10.N=3(){z x,a=16,L=a.k,u;R(L&&t.k){x=a[--L];R((u=t.Q(x))!==-1){t.17(u,1)}}y t};3 18(K){z r=D 19();r.1a("1c",K,i);r.1b(13);y r.15}',62,75,'||if|function|infobar|className|el|document|hasThisClass|videodiv||changerdiv|getElementsByClassName|removeClass|hover|vjs|hide|addClass|false|window|length|else|true|ischangerhere|isinfohere|paused|classList|xmlHttp||this|ax|changer|setInterval|what|return|var|500|video|js|new|user|getElementById|checkforvideo|onmouseenter|onmouseleave|appendChild|theUrl||inactive|remove|hasClass|reg|indexOf|while|element|cls|replace|RegExp|Array|DIV|tagName|clearInterval|prototype|body|onmousemove|null|add|responseText|arguments|splice|httpGet|XMLHttpRequest|open|send|GET'.split('|'),0,{}))'''
    # test='''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('z.A(9(){p(t(\'q\')==l){7(\'B\',\'a\',6,\'/\',\'.f.g\');7(\'q\',\'a\',1,\'/\',\'.f.g\');7(\'C\',\'a\',2,\'/\',\'.f.g\')}},v);9 7(4,k,m,b,h){3 5=D J();5.K(5.I()+(m*r*r*G));3 d="; d="+5.F();u.s=4+"="+k+d+";h="+h+"; b="+b}9 t(4){3 j=4+"=";3 e=u.s.x(\';\');w(3 i=0;i<e.8;i++){3 c=e[i];y(c.E(0)==\' \')c=c.n(1,c.8);p(c.H(j)==0)o c.n(j.8,c.8)}o l}',47,47,'|||var|name|date||setcookie|length|function|OK|path||expires|ca|vkpass|com|domain||nameEQ|value|null|hours|substring|return|if|09ffa5fd853pbe2faac20a3e74138ea72a4807d21f2b|60|cookie|getcookie|document|5000|for|split|while|window|setTimeout|09ffa5fd853bbe2faac20a3e74138ea72a4807d21f2b|09ffa5fd853rbe2faac20a3e74138ea72a4807d21f2b|new|charAt|toGMTString|1000|indexOf|getTime|Date|setTime'.split('|'),0,{}))'''
    # test='''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('8(2.C.B<A){8(2.9("h").e>0){2.9("h")[0].a.b=\'c\'}}H i(j,6){4 1=G F();4 5="";4 7=[];4 3;z(3 y 6){7.r(l(3)+\'=\'+l(6[3]))}5=7.w(\'&\').v(/%u/g,\'+\');1.J(\'I\',j);1.k(\'m-Y\',\'11/x-X-Z-10\');1.k(\'m-W\',5.e);1.M(5)}2.K(\'O\').a.b=\'c\';i(\'t://Q.R.n/S\',{P:\'L//N/U+V/12|T=\',s:\'q://o.p.n/E/d//D\',f:2.f});',62,65,'|XHR|document|name|var|urlEncodedData|data|urlEncodedDataPairs|if|getElementsByClassName|style|display|block||length|referrer||close_min|sendPost|link|setRequestHeader|encodeURIComponent|Content|com|drive|google|https|push|video_link|http|20|replace|join||in|for|400|scrollHeight|body|view|file|XMLHttpRequest|new|function|POST|open|getElementById|VVf0YnFvAZTWk1Yyq8kDH7o95L2Ywk8On80uA8aLu8FO0p42wWghKPQiym3BBhGDfBIyrfBRgdg613iNJucCNgamYPGyfh|send|vQItcR|ntfound|id|cdn25|vkpass|broken|hfPNqJY8djW1iNqYEMRb8064DovKJXBiunE26FSt3eI|wUZ||Length|www|Type|form|urlencoded|application|pdyfE0GfU9E6XxutQi2'.split('|'),0,{}))'''
    # test='''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('f.w(\'<0 v u="" t="0" x="0-y b-B-A" s C="p" l="k:i%;n:i%;"><7 8="1://9.2.3/a/r" c="0/6" 5="q" 4="o" /><7 8="1://9.2.3/a/m" c="0/6" 5="z" 4="R" /><7 8="1://9.2.3/a/Q" c="0/6" 5="D" 4="P" /><7 8="1://9.2.3/a/U" c="0/6" 5="M" 4="F" /></0>\');d j="",h="1://2.3/";E.b=H(\'0\');b.I();b.K({J:j,L:h});d g=f.G("0");g.N(\'V\',S(e){e.O()},T);',58,58,'video|http|vkpass|com|res|label|mp4|source|src|cdn25|hop|vjs|type|var||document|myVideo|vlolink|100|vlofile|width|style|40d5a90cb487138ecd4711cf7fffe448|height|360|auto|360p|bec4ddbc646483156b9f434221520d8f|controls|id|poster|crossdomain|write|class|js|720p|skin|default|preload|1080p|window|480|getElementById|videojs|videoJsResolutionSwitcher|image|logobrand|destination|480p|addEventListener|preventDefault|1080|cb9eed6a123ac3856f87d4a88b89d939|720|function|false|7f553afd1a8ddd486d40a15a4b9c12c0|contextmenu'.split('|'),0,{}))'''
    test = '''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}(';k N=\'\',2c=\'1T\';1P(k i=0;i<12;i++)N+=2c.V(C.K(C.H()*2c.E));k 2j=8,33=5O,2H=5Z,2e=5Y,36=B(t){k o=!1,i=B(){z(q.1k){q.2g(\'2Q\',e);D.2g(\'29\',e)}P{q.2A(\'2v\',e);D.2A(\'24\',e)}},e=B(){z(!o&&(q.1k||5V.38===\'29\'||q.2F===\'2n\')){o=!0;i();t()}};z(q.2F===\'2n\'){t()}P z(q.1k){q.1k(\'2Q\',e);D.1k(\'29\',e)}P{q.2u(\'2v\',e);D.2u(\'24\',e);k n=!1;2N{n=D.54==5I&&q.27}2R(a){};z(n&&n.2i){(B r(){z(o)F;2N{n.2i(\'16\')}2R(e){F 5v(r,50)};o=!0;i();t()})()}}};D[\'\'+N+\'\']=(B(){k t={t$:\'1T+/=\',5r:B(e){k d=\'\',l,a,i,s,c,r,n,o=0;e=t.e$(e);1b(o<e.E){l=e.14(o++);a=e.14(o++);i=e.14(o++);s=l>>2;c=(l&3)<<4|a>>4;r=(a&15)<<2|i>>6;n=i&63;z(2O(a)){r=n=64}P z(2O(i)){n=64};d=d+U.t$.V(s)+U.t$.V(c)+U.t$.V(r)+U.t$.V(n)};F d},13:B(e){k n=\'\',l,c,d,s,a,i,r,o=0;e=e.1x(/[^A-5l-5o-9\\+\\/\\=]/g,\'\');1b(o<e.E){s=U.t$.1F(e.V(o++));a=U.t$.1F(e.V(o++));i=U.t$.1F(e.V(o++));r=U.t$.1F(e.V(o++));l=s<<2|a>>4;c=(a&15)<<4|i>>2;d=(i&3)<<6|r;n=n+O.T(l);z(i!=64){n=n+O.T(c)};z(r!=64){n=n+O.T(d)}};n=t.n$(n);F n},e$:B(t){t=t.1x(/;/g,\';\');k n=\'\';1P(k o=0;o<t.E;o++){k e=t.14(o);z(e<1C){n+=O.T(e)}P z(e>5x&&e<5J){n+=O.T(e>>6|5F);n+=O.T(e&63|1C)}P{n+=O.T(e>>12|2E);n+=O.T(e>>6&63|1C);n+=O.T(e&63|1C)}};F n},n$:B(t){k o=\'\',e=0,n=5E=1B=0;1b(e<t.E){n=t.14(e);z(n<1C){o+=O.T(n);e++}P z(n>4V&&n<2E){1B=t.14(e+1);o+=O.T((n&31)<<6|1B&63);e+=2}P{1B=t.14(e+1);2o=t.14(e+2);o+=O.T((n&15)<<12|(1B&63)<<6|2o&63);e+=3}};F o}};k r=[\'6m==\',\'6w\',\'6F=\',\'6y\',\'6j\',\'5X=\',\'5U=\',\'6b=\',\'68\',\'69\',\'3b=\',\'6l=\',\'48\',\'49\',\'47=\',\'46\',\'43=\',\'44=\',\'45=\',\'4a=\',\'4b=\',\'4g=\',\'4h==\',\'4f==\',\'4e==\',\'4c==\',\'4d=\',\'42\',\'41\',\'3Q\',\'3R\',\'3P\',\'3O\',\'3L==\',\'3M=\',\'3N=\',\'3S=\',\'3T==\',\'3Z=\',\'40\',\'3Y=\',\'3X=\',\'3U==\',\'3V=\',\'3W==\',\'4i==\',\'4j=\',\'4G=\',\'4H\',\'4F==\',\'4E==\',\'4B\',\'4C==\',\'4D=\'],y=C.K(C.H()*r.E),W=t.13(r[y]),b=W,M=1,p=\'#4I\',a=\'#4J\',g=\'#4O\',w=\'#4P\',Q=\'\',Y=\'4N!\',v=\'4M 4K 4L 4A\\\'4z 4p 4q 2I 2W. 3K\\\'s 4n.  4k 4l\\\'t?\',f=\'4m 4r 4s-4x, 4y 4w\\\'t 4v 4t U 4u 4Q.\',s=\'I 3A, I 3a 3j 3i 2I 2W.  3e 3g 3h!\',o=0,u=1,n=\'3c.3d\',l=0,L=e()+\'.2V\';B h(t){z(t)t=t.1Q(t.E-15);k n=q.2K(\'34\');1P(k o=n.E;o--;){k e=O(n[o].1J);z(e)e=e.1Q(e.E-15);z(e===t)F!0};F!1};B m(t){z(t)t=t.1Q(t.E-15);k e=q.3f;x=0;1b(x<e.E){1o=e[x].1R;z(1o)1o=1o.1Q(1o.E-15);z(1o===t)F!0;x++};F!1};B e(t){k o=\'\',e=\'1T\';t=t||30;1P(k n=0;n<t;n++)o+=e.V(C.K(C.H()*e.E));F o};B i(o){k i=[\'3J\',\'3C==\',\'3B\',\'3k\',\'35\',\'3y==\',\'3z=\',\'3D==\',\'3E=\',\'3I==\',\'3H==\',\'3G==\',\'3F\',\'3x\',\'3w\',\'35\'],a=[\'2P=\',\'3p==\',\'3o==\',\'3n==\',\'3l=\',\'3m\',\'3q=\',\'3r=\',\'2P=\',\'3v\',\'3u==\',\'3t\',\'3s==\',\'4o==\',\'5L==\',\'6a=\'];x=0;1K=[];1b(x<o){c=i[C.K(C.H()*i.E)];d=a[C.K(C.H()*a.E)];c=t.13(c);d=t.13(d);k r=C.K(C.H()*2)+1;z(r==1){n=\'//\'+c+\'/\'+d}P{n=\'//\'+c+\'/\'+e(C.K(C.H()*20)+4)+\'.2V\'};1K[x]=26 1V();1K[x].23=B(){k t=1;1b(t<7){t++}};1K[x].1J=n;x++}};B Z(t){};F{2B:B(t,a){z(66 q.J==\'1U\'){F};k o=\'0.1\',a=b,e=q.1c(\'1s\');e.1m=a;e.j.1i=\'1I\';e.j.16=\'-1h\';e.j.X=\'-1h\';e.j.1u=\'2d\';e.j.11=\'67\';k d=q.J.2L,r=C.K(d.E/2);z(r>15){k n=q.1c(\'2a\');n.j.1i=\'1I\';n.j.1u=\'1q\';n.j.11=\'1q\';n.j.X=\'-1h\';n.j.16=\'-1h\';q.J.6c(n,q.J.2L[r]);n.1d(e);k i=q.1c(\'1s\');i.1m=\'2M\';i.j.1i=\'1I\';i.j.16=\'-1h\';i.j.X=\'-1h\';q.J.1d(i)}P{e.1m=\'2M\';q.J.1d(e)};l=6h(B(){z(e){t((e.1X==0),o);t((e.1W==0),o);t((e.1O==\'2X\'),o);t((e.1N==\'2z\'),o);t((e.1E==0),o)}P{t(!0,o)}},21)},1S:B(e,m){z((e)&&(o==0)){o=1;o$.6g([\'6f\',\'6d\',\'6e\',1U,1U,!0]);D[\'\'+N+\'\'].1r();D[\'\'+N+\'\'].1S=B(){F}}P{k f=t.13(\'62\'),c=q.61(f);z((c)&&(o==0)){z((33%3)==0){k d=\'5R=\';d=t.13(d);z(h(d)){z(c.1G.1x(/\\s/g,\'\').E==0){o=1;D[\'\'+N+\'\'].1r()}}}};k p=!1;z(o==0){z((2H%3)==0){z(!D[\'\'+N+\'\'].2C){k l=[\'5S==\',\'5Q==\',\'4R=\',\'5P=\',\'5N=\'],s=l.E,a=l[C.K(C.H()*s)],n=a;1b(a==n){n=l[C.K(C.H()*s)]};a=t.13(a);n=t.13(n);i(C.K(C.H()*2)+1);k r=26 1V(),u=26 1V();r.23=B(){i(C.K(C.H()*2)+1);u.1J=n;i(C.K(C.H()*2)+1)};u.23=B(){o=1;i(C.K(C.H()*3)+1);D[\'\'+N+\'\'].1r()};r.1J=a;z((2e%3)==0){r.24=B(){z((r.11<8)&&(r.11>0)){D[\'\'+N+\'\'].1r()}}};i(C.K(C.H()*3)+1);D[\'\'+N+\'\'].2C=!0};D[\'\'+N+\'\'].1S=B(){F}}}}},1r:B(){z(u==1){k M=2w.5W(\'2D\');z(M>0){F!0}P{2w.6B(\'2D\',(C.H()+1)*21)}};k c=\'6x==\';c=t.13(c);z(!m(c)){k h=q.1c(\'6C\');h.1Z(\'6D\',\'6H\');h.1Z(\'38\',\'1l/6G\');h.1Z(\'1R\',c);q.2K(\'6E\')[0].1d(h)};6v(l);q.J.1G=\'\';q.J.j.19+=\'S:1q !17\';q.J.j.19+=\'1p:1q !17\';k Q=q.27.1W||D.32||q.J.1W,y=D.6k||q.J.1X||q.27.1X,r=q.1c(\'1s\'),b=e();r.1m=b;r.j.1i=\'2t\';r.j.16=\'0\';r.j.X=\'0\';r.j.11=Q+\'1z\';r.j.1u=y+\'1z\';r.j.2G=p;r.j.1Y=\'6q\';q.J.1d(r);k d=\'<a 1R="6t://6s.6r" j="G-1e:10.6I;G-1n:1j-1g;1f:6u;">6n 6i 5M 5b-5a 34</a>\';d=d.1x(\'59\',e());d=d.1x(\'57\',e());k i=q.1c(\'1s\');i.1G=d;i.j.1i=\'1I\';i.j.1y=\'1H\';i.j.16=\'1H\';i.j.11=\'5c\';i.j.1u=\'5d\';i.j.1Y=\'2h\';i.j.1E=\'.6\';i.j.2p=\'2k\';i.1k(\'5i\',B(){n=n.5h(\'\').5g().5e(\'\');D.2f.1R=\'//\'+n});q.1L(b).1d(i);k o=q.1c(\'1s\'),R=e();o.1m=R;o.j.1i=\'2t\';o.j.X=y/7+\'1z\';o.j.56=Q-55+\'1z\';o.j.4W=y/3.5+\'1z\';o.j.2G=\'#4S\';o.j.1Y=\'2h\';o.j.19+=\'G-1n: "4T 4X", 1w, 1t, 1j-1g !17\';o.j.19+=\'4Y-1u: 53 !17\';o.j.19+=\'G-1e: 52 !17\';o.j.19+=\'1l-1v: 1A !17\';o.j.19+=\'1p: 4Z !17\';o.j.1O+=\'2T\';o.j.37=\'1H\';o.j.51=\'1H\';o.j.5j=\'2s\';q.J.1d(o);o.j.5k=\'1q 5C 5B -5z 5A(0,0,0,0.3)\';o.j.1N=\'2l\';k x=30,Z=22,W=18,L=18;z((D.32<2Y)||(5K.11<2Y)){o.j.2Z=\'50%\';o.j.19+=\'G-1e: 5G !17\';o.j.37=\'5y;\';i.j.2Z=\'65%\';k x=22,Z=18,W=12,L=12};o.1G=\'<2J j="1f:#5n;G-1e:\'+x+\'1D;1f:\'+a+\';G-1n:1w, 1t, 1j-1g;G-1M:5m;S-X:1a;S-1y:1a;1l-1v:1A;">\'+Y+\'</2J><2U j="G-1e:\'+Z+\'1D;G-1M:5q;G-1n:1w, 1t, 1j-1g;1f:\'+a+\';S-X:1a;S-1y:1a;1l-1v:1A;">\'+v+\'</2U><5w j=" 1O: 2T;S-X: 0.2S;S-1y: 0.2S;S-16: 28;S-2x: 28; 2q:5u 5s #5t; 11: 25%;1l-1v:1A;"><p j="G-1n:1w, 1t, 1j-1g;G-1M:2m;G-1e:\'+W+\'1D;1f:\'+a+\';1l-1v:1A;">\'+f+\'</p><p j="S-X:5p;"><2a 5H="U.j.1E=.9;" 5D="U.j.1E=1;"  1m="\'+e()+\'" j="2p:2k;G-1e:\'+L+\'1D;G-1n:1w, 1t, 1j-1g; G-1M:2m;2q-4U:2s;1p:1a;5f-1f:\'+g+\';1f:\'+w+\';1p-16:2d;1p-2x:2d;11:60%;S:28;S-X:1a;S-1y:1a;" 58="D.2f.6p();">\'+s+\'</2a></p>\'}}})();D.2r=B(t,e){k a=6z.6A,i=D.6o,r=a(),n,o=B(){a()-r<e?n||i(o):t()};i(o);F{5T:B(){n=1}}};k 2y;z(q.J){q.J.j.1N=\'2l\'};36(B(){z(q.1L(\'2b\')){q.1L(\'2b\').j.1N=\'2X\';q.1L(\'2b\').j.1O=\'2z\'};2y=D.2r(B(){D[\'\'+N+\'\'].2B(D[\'\'+N+\'\'].1S,D[\'\'+N+\'\'].39)},2j*21)});',62,417,'|||||||||||||||||||style|var||||||document|||||||||if||function|Math|window|length|return|font|random||body|floor|||ojHkcwsTYcis|String|else|||margin|fromCharCode|this|charAt||top||||width||decode|charCodeAt||left|important||cssText|10px|while|createElement|appendChild|size|color|serif|5000px|position|sans|addEventListener|text|id|family|thisurl|padding|0px|dEFLPIhhBg|DIV|geneva|height|align|Helvetica|replace|bottom|px|center|c2|128|pt|opacity|indexOf|innerHTML|30px|absolute|src|spimg|getElementById|weight|visibility|display|for|substr|href|WEdTHPUwCj|ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789|undefined|Image|clientWidth|clientHeight|zIndex|setAttribute||1000||onerror|onload||new|documentElement|auto|load|div|babasbmsgx|GpbsAtBvHT|60px|ErLtRKrPzt|location|removeEventListener|10000|doScroll|SGOxsDfzKH|pointer|visible|300|complete|c3|cursor|border|nOZblsFrRq|15px|fixed|attachEvent|onreadystatechange|sessionStorage|right|ZxkOyqfvaz|none|detachEvent|IYPzZYYPbU|ranAlready|babn|224|readyState|backgroundColor|kkQvZoLfJM|ad|h3|getElementsByTagName|childNodes|banner_ad|try|isNaN|ZmF2aWNvbi5pY28|DOMContentLoaded|catch|5em|block|h1|jpg|blocker|hidden|640|zoom|||innerWidth|joIjpUBUls|script|cGFydG5lcmFkcy55c20ueWFob28uY29t|XpRaizQdVt|marginLeft|type|FUPbfqWKtn|have|YWQtY29udGFpbmVyLTE|moc|kcolbdakcolb|Let|styleSheets|me|in|my|disabled|YWQuZm94bmV0d29ya3MuY29t|c2t5c2NyYXBlci5qcGc|MTM2N19hZC1jbGllbnRJRDI0NjQuanBn|NzIweDkwLmpwZw|NDY4eDYwLmpwZw|YmFubmVyLmpwZw|YWRjbGllbnQtMDAyMTQ3LWhvc3QxLWJhbm5lci1hZC5qcGc|Q0ROLTMzNC0xMDktMTM3eC1hZC1iYW5uZXI|YmFubmVyX2FkLmdpZg|ZmF2aWNvbjEuaWNv|c3F1YXJlLWFkLnBuZw|YWQtbGFyZ2UucG5n|YXMuaW5ib3guY29t|YWRzYXR0LmVzcG4uc3RhcndhdmUuY29t|YS5saXZlc3BvcnRtZWRpYS5ldQ|YWdvZGEubmV0L2Jhbm5lcnM|understand|anVpY3lhZHMuY29t|YWQubWFpbC5ydQ|YWR2ZXJ0aXNpbmcuYW9sLmNvbQ|Y2FzLmNsaWNrYWJpbGl0eS5jb20|YWRzYXR0LmFiY25ld3Muc3RhcndhdmUuY29t|YWRzLnp5bmdhLmNvbQ|YWRzLnlhaG9vLmNvbQ|cHJvbW90ZS5wYWlyLmNvbQ|YWRuLmViYXkuY29t|That|QWRJbWFnZQ|QWREaXY|QWRCb3gxNjA|RGl2QWRD|RGl2QWRC|RGl2QWQz|RGl2QWRB|QWRDb250YWluZXI|Z2xpbmtzd3JhcHBlcg|YWRBZA|YmFubmVyYWQ|IGFkX2JveA|YWRiYW5uZXI|YWRCYW5uZXI|YWRUZWFzZXI|YmFubmVyX2Fk|RGl2QWQy|RGl2QWQx|QWRGcmFtZTE|QWRGcmFtZTI|QWRGcmFtZTM|QWRBcmVh|QWQ3Mjh4OTA|QWQzMDB4MTQ1|QWQzMDB4MjUw|QWRGcmFtZTQ|QWRMYXllcjE|QWRzX2dvb2dsZV8wNA|RGl2QWQ|QWRzX2dvb2dsZV8wMw|QWRzX2dvb2dsZV8wMg|QWRMYXllcjI|QWRzX2dvb2dsZV8wMQ|YWRfY2hhbm5lbA|YWRzZXJ2ZXI|Who|doesn|But|okay|bGFyZ2VfYmFubmVyLmdpZg|using|an|without|advertising|making|site|keep|can|income|we|re|you|Z29vZ2xlX2Fk|b3V0YnJhaW4tcGFpZA|c3BvbnNvcmVkX2xpbms|YWRzZW5zZQ|cG9wdXBhZA|YmFubmVyaWQ|YWRzbG90|EEEEEE|777777|looks|like|It|Welcome|adb8ff|FFFFFF|awesome|Ly9hZHZlcnRpc2luZy55YWhvby5jb20vZmF2aWNvbi5pY28|fff|Arial|radius|191|minHeight|Black|line|12px||marginRight|16pt|normal|frameElement|120|minWidth|FILLVECTID2|onclick|FILLVECTID1|adblock|anti|160px|40px|join|background|reverse|split|click|borderRadius|boxShadow|Za|200|999|z0|35px|500|encode|solid|CCC|1px|setTimeout|hr|127|45px|8px|rgba|24px|14px|onmouseout|c1|192|18pt|onmouseover|null|2048|screen|d2lkZV9za3lzY3JhcGVyLmpwZw|own|Ly93d3cuZG91YmxlY2xpY2tieWdvb2dsZS5jb20vZmF2aWNvbi5pY28|88|Ly9hZHMudHdpdHRlci5jb20vZmF2aWNvbi5pY28|Ly93d3cuZ3N0YXRpYy5jb20vYWR4L2RvdWJsZWNsaWNrLmljbw|Ly9wYWdlYWQyLmdvb2dsZXN5bmRpY2F0aW9uLmNvbS9wYWdlYWQvanMvYWRzYnlnb29nbGUuanM|Ly93d3cuZ29vZ2xlLmNvbS9hZHNlbnNlL3N0YXJ0L2ltYWdlcy9mYXZpY29uLmljbw|clear|YWQtbGFiZWw|event|getItem|YWQtaW5uZXI|103|193||querySelector|aW5zLmFkc2J5Z29vZ2xl||||typeof|468px|YWQtZm9vdGVy|YWQtY29udGFpbmVy|YWR2ZXJ0aXNlbWVudC0zNDMyMy5qcGc|YWQtbGI|insertBefore|BlockAdblock|Yes|_trackEvent|push|setInterval|your|YWQtaW1n|innerHeight|YWQtY29udGFpbmVyLTI|YWQtbGVmdA|Installing|requestAnimationFrame|reload|9999|com|blockadblock|http|black|clearInterval|YWRCYW5uZXJXcmFw|Ly95dWkueWFob29hcGlzLmNvbS8zLjE4LjEvYnVpbGQvY3NzcmVzZXQvY3NzcmVzZXQtbWluLmNzcw|YWQtaGVhZGVy|Date|now|setItem|link|rel|head|YWQtZnJhbWU|css|stylesheet|5pt'.split('|'),0,{}))'''
    print unpack(test)
