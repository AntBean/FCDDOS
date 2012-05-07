from uasparser import UASparser  
uas_parser = UASparser('/home/natty/FCDDOS/UASparserCache')  
userAgents = ["Bimbot/1.0","Mozilla/5.0 (compatible; U; ABrowse 0.6; Syllable) AppleWebKit/420+  (KHTML, like Gecko)","Mozilla/5.0 (Linux; U; Android 4.0.3; de-ch; HTC Sensation Build/IML74K)  AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30","Bunjalloo/0.7.6(Nintendo DS;U;en)","Wget/1.9+cvs-stable (Red Hat modified)","Mozilla/5.0 (X11; Linux i686; rv:7.0.1) Gecko/20110929 Thunderbird/7.0.1","Mozilla/5.0 (compatible; AbiLogicBot/1.0; +http://www.abilogic.com/bot.html)","EmailSiphon","CSE HTML Validator Lite Online (http://online.htmlvalidator.com/php/onlinevallite.php)","GreatNews/1.0","BinGet/1.00.A (http://www.bin-co.com/php/scripts/load/)","AppEngine-Google; (+http://code.google.com/appengine; appid: unblock4myspace)","AppEngine-Google; (+http://code.google.com/appengine; appid: webetrex)","amaya/11.3.1 libwww/5.4.1"]

userAgents = ['Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Win 9x4.90;http://www.Abolimba.de)',
    'GetRight/3.2',
    'Mozilla/5.0 (X11; U; Linux armv6l; rv: 1.8.1.5pre) Gecko/20070619 Minimo/0.020',
    'GcMail Browser/1.0 (compatible; MSIE 5.0; Windows 98) ',
    'Chilkat/1.0.0 (+http://www.chilkatsoft.com/ChilkatHttpUA.asp)',
    'Klondike/1.50 (HTTP Win32)',
    'HTMLParser/1.6',
    'Abilon',
    'Banshee 1.5.1 (http://banshee-project.org/)',
    'ApacheBench/2.3',
    'http://Anonymouse.org/ (Unix)',
    'Mozilla/5.0 (compatible; WASALive-Bot ; http://blog.wasalive.com/wasalive-bots/)']
for userAgent in userAgents:
    result = uas_parser.parse(userAgent)
    print result["typ"]
