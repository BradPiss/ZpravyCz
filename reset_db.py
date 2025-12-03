import os
from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.comment import Comment
from app.models.vote import Vote
from app.models.enums import Role, ArticleStatus
import app.models # Důležité: Načte všechny modely i asociační tabulky

# --- TVOJE DATA ---
articles_data = [
    {
        'title': 'Finále Ligy mistrů: Real Madrid vítězí',
        'perex': 'Real Madrid to znovu dokázal. Ve finále Ligy mistrů proti Liverpoolu rozhodl jediný gól v nastavení. Bílý balet tak slaví už patnáctou trofej v nejprestižnější klubové soutěži, přestože v zápase tahal většinu času za kratší konec.', 
        'content': '<p>Zápas, který se odehrál v londýnském Wembley, nabídl od prvních minut taktickou bitvu. Zatímco anglický celek tlačil a vytvářel si šance, obrana Realu v čele s bezchybným brankářem dlouho odolávala. Thibaut Courtois předvedl několik zákroků, které se jistě zapíší do historie finálových duelů. Liverpool nastřelil dvakrát tyč, ale štěstěna stála na straně španělského giganta.</p>\r\n\r\n<p>Rozhodnutí přišlo v momentě, kdy už se všichni na stadionu i u televizních obrazovek chystali na prodloužení. V 92. minutě unikl po křídle Vinícius Júnior, který přesným centrem našel ve vápně střídajícího žolíka. Ten nekompromisní hlavičkou nedal brankáři Alissonovi šanci. Stadion explodoval nadšením v sektoru fanoušků Realu, zatímco na lavičce Liverpoolu zavládlo hrobové ticho.</p>\r\n\r\n<p>„Tohle je Real Madrid. Nikdy se nevzdáváme, i když to vypadá beznadějně. Máme to v DNA,“ prohlásil po zápase trenér Carlo Ancelotti, který se stal prvním trenérem v historii s pěti tituly z Ligy mistrů. Oslavy v Madridu se očekávají bouřlivé a potrvají až do ranních hodin.</p>',
        'image_url': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?q=80&w=1000',
        'home_position': 1,
        'category_name': 'Sport',
    },
    {
        'title': 'Nová linka metra D se otevírá',
        'perex': 'Pražané se dočkali. Dlouho vyhlížená linka metra D dnes zahajuje provoz s cestujícími. Automatické vlaky bez řidiče spojí centrum s jihem metropole a výrazně ulehčí dopravě z Písnice.',
        'content': '<p>Slavnostního přestřižení pásky se dnes v dopoledních hodinách zúčastnili zástupci města i dopravního podniku. První úsek, který zahrnuje pět stanic, je specifický nejen svou architekturou, ale především technologiemi. Metro D je totiž první plně automatizovanou linkou v České republice. Vlaky jezdí bez řidičů, což cestujícím nabízí unikátní výhled čelním oknem přímo do tunelu.</p>\r\n\r\n<p>Interiéry stanic byly navrženy s důrazem na moderní umění. Každá stanice má svůj specifický vizuální styl, na kterém se podíleli přední čeští výtvarníci. Například stanice Olbrachtova zaujme velkoformátovými malbami, zatímco Pankrác, která slouží jako přestupní uzel na linku C, sází na futuristické osvětlení a prosklené bezpečnostní stěny na nástupišti.</p>\r\n\r\n<p>Otevření linky však provázejí i drobné obavy. Odborníci upozorňují, že v prvních týdnech může docházet k technickým laděním systému. Dopravní podnik nicméně ujišťuje, že bezpečnost je na prvním místě a vlaky prošly tisíci hodinami testovacích jízd bez pasažérů. Plný provoz bez omezení by měl naběhnout během následujícího měsíce.</p>',
        'image_url': 'https://d15-a.sdn.cz/d_15/c_img_F_E/OosBqcL.jpeg',
        'home_position': 2,
        'category_name': 'Domácí',
    },
    {
        'title': 'Průlom v umělé inteligenci',
        'perex': 'Vědci představili nový model umělé inteligence, který předpovídá počasí s přesností na minuty. Systém MeteoMind překonává dosavadní superpočítače a může znamenat revoluci v dopravě i zemědělství.',
        'content': '<p>Nový model, vyvinutý ve spolupráci několika evropských univerzit a technologických gigantů, funguje na principu hlubokého strojového učení. Na rozdíl od klasických numerických modelů, které simulují fyzikální procesy v atmosféře, se tato umělá inteligence učí z historických dat a satelitních snímků v reálném čase. Dokáže tak identifikovat vzorce bouřek či krupobití, které byly dosud nepředvídatelné.</p>\r\n\r\n<p>„Představte si, že vám telefon oznámí, že přesně za tři minuty začne na vaší zahradě pršet, a bude mít pravdu s 99% pravděpodobností. To už není sci-fi, to je realita, kterou tento model přináší,“ uvedl vedoucí výzkumného týmu Dr. Thomas Weber. Technologie by měla být integrována do běžných meteorologických aplikací během příštího roku.</p>\r\n\r\n<p>Kromě pohodlí pro běžné uživatele má objev obrovský dopad na bezpečnost. Systém dokáže varovat před bleskovými povodněmi nebo tornády mnohem dříve, než to dokážou současné radary. Kritici však varují před přílišnou závislostí na AI a upozorňují na energetickou náročnost trénování takto komplexních modelů.</p>',
        'image_url': 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1000',
        'home_position': 3,
        'category_name': 'Technologie',
    },
    {
        'title': 'Ceny másla v Česku opět rostou',
        'perex': 'Cena másla v českých obchodech opět roste a překročila hranici 60 korun. Ekonomové varují, že před Vánoci může zdražování základních potravin pokračovat kvůli nedostatku tuku na trhu.',
        'content': '<p>Podle údajů Českého statistického úřadu zdražilo máslo meziměsíčně o téměř deset procent. Mlékárny tento nárůst zdůvodňují nižší tučností mléka v letních měsících, ale také vysokými cenami energií a krmiv. „Situace je napjatá v celé Evropě. Poptávka po smetaně je obrovská a český trh je silně provázaný s německým, kde ceny rovněž stoupají,“ vysvětluje agrární analytik Petr Havel.</p>\r\n\r\n<p>Obchodní řetězce se brání, že pouze promítají nákupní ceny do konečných cen pro spotřebitele. Zákazníci však reagují podrážděně. Na sociálních sítích se množí fotografie cenovek z pohraničí, kde je máslo v přepočtu často levnější, a to i navzdory vyšší kupní síle sousedů v Polsku či Německu. Mnozí Češi tak opět plánují předvánoční nákupy za hranicemi.</p>\r\n\r\n<p>Co to znamená pro vánoční pečení? Cukráři odhadují, že cena vánočního cukroví letos vzroste zhruba o 15 až 20 procent. Lidé pravděpodobně sáhnou po levnějších náhražkách, jako jsou rostlinné tuky, nebo omezí množství napečeného cukroví. Odborníci doporučují sledovat slevové akce, ale zároveň varují před panickými nákupy, které by ceny mohly vyhnat ještě výše.</p>',
        'image_url': 'https://d15-a.sdn.cz/d_15/c_img_m3_A/nEEmzB06yDtMFlcR24Hy/aabd.jpeg',
        'home_position': 4,
        'category_name': 'Ekonomika',
    },
    {
        'title': 'Zemětřesení v Japonsku nezpůsobilo škody',
        'perex': 'Severovýchod Japonska v noci zasáhlo silné zemětřesení o síle 6,8 stupně. Úřady sice vydaly varování před tsunami, k velkým škodám ani ztrátám na životech ale podle prvních zpráv nedošlo.',
        'content': '<p>Epicentrum se nacházelo v moři nedaleko prefektury Fukušima, což okamžitě vyvolalo obavy o bezpečnost tamní jaderné elektrárny. Provozovatel elektrárny TEPCO však krátce po otřesech vydal prohlášení, že všechny systémy jsou stabilní a nedošlo k žádnému úniku radiace. Preventivně byly odstaveny některé vlakové spoje šinkansen, které se po kontrole tratí opět rozjely.</p>\r\n\r\n<p>Japonská infrastruktura opět prokázala svou neuvěřitelnou odolnost. Budovy ve větších městech se pouze rozkývaly, ale díky speciálním tlumícím systémům zůstaly nepoškozené. „Byl to silný a dlouhý otřes, vypadly nám knihy z polic, ale elektřina i voda fungují,“ popsala situaci obyvatelka města Sendai pro místní televizi NHK.</p>',
        'image_url': 'https://d15-a.sdn.cz/d_15/c_img_QK_6/v9jJz/japonsko.jpeg',
        'home_position': 0,
        'category_name': 'Zahraničí',
    },
    {
        'title': 'Tesla svolává tisíce vozů',
        'perex': 'Tesla svolává do servisů přes dvě stě tisíc vozů Model 3 a Y. Důvodem je riziko samovolného otevření přední kapoty za jízdy. Většinu problémů ale vyřeší aktualizace softwaru.',
        'content': '<p>Problém se týká vozů vyrobených v posledních třech letech. Podle zprávy pro americký úřad pro bezpečnost silničního provozu (NHTSA) může dojít k selhání západky sekundárního zámku. Tesla sice neeviduje žádné nehody způsobené touto závadou, přesto přistoupila k preventivnímu opatření, aby předešla riziku.</p>\r\n\r\n<p>Dobrou zprávou pro majitele je, že ve většině případů nebude nutná návštěva servisu. Automobilka plánuje problém vyřešit prostřednictvím bezdrátové softwarové aktualizace (OTA), která upraví senzory detekce otevřené kapoty a přidá varování pro řidiče. Akcie společnosti na zprávu reagovaly mírným poklesem, ale analytici nepředpokládají dlouhodobý dopad na prodeje značky.</p>',
        'image_url': 'https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=1000',
        'home_position': 0,
        'category_name': 'Technologie',
    },
    {
        'title': 'Čeští hokejisté zahájili přípravu',
        'perex': 'Hokejová reprezentace zahájila přípravu na blížící se mistrovství světa. Trenér Radim Rulík přivítal na srazu v Českých Budějovicích první hráče, na posily z NHL se zatím čeká.',
        'content': '<p>„Kluci přijeli s chutí, to je pro mě nejdůležitější. Máme před sebou měsíc tvrdé práce, musíme vyladit systém a najít tu správnou chemii,“ řekl novinářům Rulík po prvním tréninku na ledě. V týmu zatím chybí největší hvězdy z NHL, jejichž účast je závislá na vývoji play-off v zámoří a výstupních prohlídkách v klubech.</p>\r\n\r\n<p>Fanoušci netrpělivě vyhlížejí zejména zprávy o Davidu Pastrňákovi. Vedení reprezentace je s bostonským kanonýrem v kontaktu, ale konkrétní příslib zatím nepadl. Mezi nominovanými je i několik nováčků, kteří si skvělými výkony v extralize řekli o pozornost a budou bojovat o místo na soupisce pro šampionát, který se letos koná ve Švédsku.</p>',
        'image_url': 'https://d15-a.sdn.cz/d_15/c_img_oZ_A/nsLxLojIBzXhfH1hDNv9NT/0670.jpeg',
        'home_position': 0,
        'category_name': 'Sport',
    },
    {
        'title': 'Inflace klesá, hypotéky by mohly zlevnit',
        'perex': 'Inflace klesá rychleji, než se čekalo, a blíží se k cíli centrální banky. To dává naději na brzké snížení úrokových sazeb, což by mohlo konečně zlevnit hypotéky a oživit realitní trh.',
        'content': '<p>Guvernér ČNB naznačil, že pokud bude tento trend pokračovat, bankovní rada by mohla přistoupit ke snížení základní úrokové sazby již na příštím zasedání. „Nechceme nic uspěchat, ale data hovoří jasně. Cenová hladina se stabilizuje,“ uvedl. Komerční banky by na tento krok měly reagovat zlevněním hypoték, které se v posledních dvou letech staly pro běžné rodiny téměř nedostupné.</p>\r\n\r\n<p>Realitní makléři už nyní pozorují oživení trhu. „Lidé, kteří vyčkávali, začínají opět chodit na prohlídky. Vědí, že ceny nemovitostí dolů nepůjdou, a tak čekají alespoň na lepší úrok,“ říká majitel jedné z pražských realitních kanceláří. Odborníci přesto radí s fixací úroků opatrnost a doporučují spíše kratší fixační období v očekávání dalšího poklesu sazeb v příštím roce.</p>',
        'image_url': 'https://images.unsplash.com/photo-1580519542036-c47de6196ba5?q=80&w=1000',
        'home_position': 0,
        'category_name': 'Ekonomika',
    },
    {
        'title': 'Nový iPhone překvapil výdrží',
        'perex': 'První testy nového iPhonu přinášejí překvapení. Díky úspornějšímu čipu vydrží telefon na jedno nabití o tři hodiny déle než předchůdce, což z něj dělá rekordmana ve své třídě.',
        'content': '<p>Technologičtí novináři, kteří měli možnost telefon testovat týden před zahájením prodeje, si pochvalují zejména optimalizaci systému iOS. I při náročném používání, jako je natáčení 4K videa nebo hraní her, se telefon nepřehřívá a procenta baterie ubývají pomaleji. „Konečně iPhone, se kterým můžete vyrazit na víkend bez powerbanky, pokud se trochu uskromníte,“ píše server The Verge.</p>\r\n\r\n<p>Design telefonu doznal jen kosmetických změn, hlavní novinkou je kromě baterie také vylepšený teleobjektiv a nové tlačítko "Action Button", které nahradilo ikonický přepínač tichého režimu. Cena nového modelu zůstává stejná jako loni, což je vzhledem k inflaci příjemným překvapením. Předobjednávky trhají rekordy.</p>',
        'image_url': 'https://images.unsplash.com/photo-1512054502232-10a0a035d672?q=80&w=1000',
        'home_position': 0,
        'category_name': 'Technologie',
    },
    {
        'title': 'Slavia v derby rozdrtila Spartu',
        'perex': 'Slavia ovládla 309. derby pražských „S“. V Edenu nedala Spartě šanci a zvítězila vysoko 4:0. Hosté dohrávali zápas v deseti a přišli o vedení v tabulce.',
        'content': '<p>Zápas začal ve vysokém tempu a Slavia šla do vedení už v 10. minutě po rohovém kopu. Sparta se snažila odpovědět, ale její útočné snahy troskotaly na pevné obraně domácích. Zlomový moment přišel těsně před přestávkou, kdy hostující stoper zatáhl za záchrannou brzdu a viděl červenou kartu. Z následné penalty zvýšila Slavia na 2:0.</p>\r\n\r\n<p>Druhý poločas už byl exhibicí domácího celku. Vyprodaný stadion hnal své hráče dopředu a ti přidali další dva góly po krásných kombinacích. „Dnes nám vyšlo úplně všechno. Cítili jsme energii z tribun a chtěli jsme to fanouškům vrátit,“ radoval se po zápase trenér Jindřich Trpišovský. Pro Spartu je to naopak krutá facka před důležitým pohárovým utkáním v Evropě.</p>',
        'image_url': 'https://www.ruik.cz/wp-content/uploads/Tomas-Chory-Slavia-Praha-7.jpg',
        'home_position': 0,
        'category_name': 'Sport',
    },
]

def reset_database():
    print("🧨 Mazání staré databáze...")
    if os.path.exists("news.db"):
        try:
            os.remove("news.db")
        except PermissionError:
            print("❌ CHYBA: Vypni server (Ctrl+C) a zkus to znovu!")
            return
    
    print("🏗️  Vytváření tabulek...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("👤 Vytváření uživatelů...")
    admin = User(email="admin@zpravy.cz", name="Hlavní Admin", password_hash=hash_password("tajneheslo123"), role=Role.ADMIN, is_active=True)
    sef = User(email="sef@zpravy.cz", name="Karel Šéf", password_hash=hash_password("sef123"), role=Role.CHIEF_EDITOR, is_active=True)
    redaktor = User(email="jan.novak@zpravy.cz", name="Jan Novák", password_hash=hash_password("redaktor123"), role=Role.EDITOR, is_active=True)
    ctenar = User(email="pepa@mail.cz", name="Pepa Zdepa", password_hash=hash_password("pepa123"), role=Role.READER, is_active=True)
    
    db.add_all([admin, sef, redaktor, ctenar])
    db.commit()
    
    print("📂 Vytváření kategorií...")
    categories = {}
    cat_names = set(a['category_name'] for a in articles_data)
    for name in cat_names:
        c = Category(name=name, description=f"Zprávy z rubriky {name}")
        db.add(c)
        categories[name] = c
    db.commit() # Abychom měli ID kategorií
    
    print(f"📰 Vytváření {len(articles_data)} článků...")
    now = datetime.now(timezone.utc)
    
    created_objects = []
    
    for i, data in enumerate(articles_data):
        cat = categories.get(data['category_name'])
        
        # Logika pro last_promoted_at (pokud je hlavní)
        last_promoted = now if data['home_position'] == 1 else None
        
        art = Article(
            title=data['title'],
            perex=data['perex'],
            content=data['content'],
            image_url=data['image_url'],
            status=ArticleStatus.PUBLISHED,
            home_position=data['home_position'],
            last_promoted_at=last_promoted,
            author_id=redaktor.id,
            category_id=cat.id,
            created_at=now - timedelta(hours=i)
        )
        created_objects.append(art)
        db.add(art)
    
    db.commit() # Uložíme články
    
    # --- PŘIDÁNÍ OBLÍBENÝCH (FAVORITES) ---
    print("⭐ Vytváření testovacích oblíbených článků...")
    
    # Najdeme články pro uložení (třeba první dva)
    article1 = created_objects[0]
    article2 = created_objects[1]
    
    # Uživatel "Pepa" (čtenář) si je uloží
    ctenar.saved_articles_rel.append(article1)
    ctenar.saved_articles_rel.append(article2)
    
    db.commit()
    
    print("✅ HOTOVO! Databáze je kompletně obnovena.")
    db.close()

if __name__ == "__main__":
    reset_database()