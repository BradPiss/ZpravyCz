import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from datetime import datetime, timezone, timedelta
from app.models.db import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.enums import Role, ArticleStatus

articles_data = [
    {
        'title': 'Optimismus investorů žene americké akcie k historickým maximům',
        'perex': 'Newyorská burza zažívá jedno z nejlepších období za poslední měsíce. Kombinace zpomalující inflace a překvapivě silných dat z trhu práce vlévá investorům do žil novou naději.',
        'content': '<p>Fasáda slavné budovy New York Stock Exchange (NYSE) na dolním Manhattanu je zahalena do obří americké vlajky, což symbolicky podtrhuje současnou vítěznou náladu na trzích. Hlavní americké akciové indexy tento týden prolomily psychologické hranice, kterým odolávaly od začátku roku. Investoři sází na to, že americká ekonomika se vyhne recesi a směřuje k takzvanému „měkkému přistání“.</p><p>Hnacím motorem současné rallye je především technologický sektor. Společnosti zabývající se umělou inteligencí a výrobou čipů vykazují nad očekávání dobré čtvrtletní výsledky, což táhne vzhůru celý trh. Analytici z Wall Street upozorňují, že důvěra v americké inovace momentálně u obchodníků přebíjí obavy z geopolitického napětí ve světě.</p><p>Pozitivní vlna z USA se okamžitě přelila i do zahraničí. Evropské i asijské burzy reagovaly na ranní otevření růstem a posiluje i americký dolar. Ekonomové však zůstávají obezřetní a varují, že nadšení může být předčasné, pokud centrální banka (Fed) nezmění svou úrokovou politiku. Přesto je pohled na vlající hvězdy a pruhy v srdci finančního světa pro tuto chvíli jasným signálem: americký finanční býk je zpět v síle.</p>',
        'image_url': 'https://sebgroup.com/imagevault/publishedmedia/vu3022l517vqvpf8g44m/SEB20220919_0684_v001.jpg',
        'image_caption': 'Americká vlajka v New Yorku',
        'category_name': 'Ekonomika',
        'home_position': 1
    },
    {
        'title': 'Finále Ligy mistrů: Real Madrid vítězí',
        'perex': 'Real Madrid to znovu dokázal. Ve finále Ligy mistrů proti Liverpoolu rozhodl jediný gól v nastavení. Bílý balet tak slaví už patnáctou trofej v nejprestižnější klubové soutěži.', 
        'content': '<p>Zápas, který se odehrál v londýnském Wembley, nabídl od prvních minut taktickou bitvu. Zatímco anglický celek tlačil a vytvářel si šance, obrana Realu v čele s bezchybným brankářem dlouho odolávala. Thibaut Courtois předvedl několik zákroků, které se jistě zapíší do historie finálových duelů.</p><p>Rozhodnutí přišlo v momentě, kdy už se všichni na stadionu i u televizních obrazovek chystali na prodloužení. V 92. minutě unikl po křídle Vinícius Júnior, který přesným centrem našel ve vápně střídajícího žolíka.</p>',
        'image_url': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?q=80&w=1000',
        'image_caption': 'Radost hráčů Realu Madrid',
        'category_name': 'Sport',
        'home_position': 2
    },
    {
        'title': 'Nová linka metra D se otevírá',
        'perex': 'Pražané se dočkali. Dlouho vyhlížená linka metra D dnes zahajuje provoz s cestujícími. Automatické vlaky bez řidiče spojí centrum s jihem metropole.',
        'content': '<p>Slavnostního přestřižení pásky se dnes v dopoledních hodinách zúčastnili zástupci města i dopravního podniku. První úsek, který zahrnuje pět stanic, je specifický nejen svou architekturou, ale především technologiemi.</p><p>Interiéry stanic byly navrženy s důrazem na moderní umění. Každá stanice má svůj specifický vizuální styl, na kterém se podíleli přední čeští výtvarníci.</p>',
        'image_url': 'https://d15-a.sdn.cz/d_15/c_img_F_E/OosBqcL.jpeg?fl=cro,0,0,800,450|res,1280,,1|webp,75',
        'image_caption': 'Pohled do tunelu nové linky',
        'category_name': 'Domácí',
        'home_position': 3
    },
    {
        'title': 'Průlom v umělé inteligenci',
        'perex': 'Vědci představili nový model umělé inteligence, který předpovídá počasí s přesností na minuty. Systém MeteoMind překonává dosavadní superpočítače.',
        'content': '<p>Nový model, vyvinutý ve spolupráci několika evropských univerzit a technologických gigantů, funguje na principu hlubokého strojového učení. Na rozdíl od klasických numerických modelů se učí z historických dat.</p>',
        'image_url': 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1000',
        'image_caption': 'Vizualizace neuronové sítě',
        'category_name': 'Technologie',
        'home_position': 4
    },
    {
        'title': 'Ceny másla v Česku opět rostou',
        'perex': 'Cena másla v českých obchodech opět roste a překročila hranici 60 korun. Ekonomové varují, že před Vánoci může zdražování základních potravin pokračovat.',
        'content': '<p>Podle údajů Českého statistického úřadu zdražilo máslo meziměsíčně o téměř deset procent. Mlékárny tento nárůst zdůvodňují nižší tučností mléka v letních měsících a cenami energií.</p>',
        'image_url': 'https://d15-a.sdn.cz/d_15/c_img_m3_A/nEEmzB06yDtMFlcR24Hy/aabd.jpeg',
        'image_caption': 'Ilustrační snímek',
        'category_name': 'Ekonomika',
        'home_position': 0
    },
    {
        'title': 'Zemětřesení v Japonsku nezpůsobilo škody',
        'perex': 'Severovýchod Japonska v noci zasáhlo silné zemětřesení o síle 6,8 stupně. Úřady sice vydaly varování před tsunami, k velkým škodám nedošlo.',
        'content': '<p>Epicentrum se nacházelo v moři nedaleko prefektury Fukušima. Provozovatel elektrárny TEPCO vydal prohlášení, že všechny systémy jsou stabilní.</p>',
        'image_url': 'https://d15-a.sdn.cz/d_15/c_img_QK_6/v9jJz/japonsko.jpeg',
        'image_caption': 'Japonské pobřeží',
        'category_name': 'Zahraničí',
        'home_position': 0
    },
    {
        'title': 'Tesla svolává tisíce vozů',
        'perex': 'Tesla svolává do servisů přes dvě stě tisíc vozů Model 3 a Y. Důvodem je riziko samovolného otevření přední kapoty za jízdy.',
        'content': '<p>Problém se týká vozů vyrobených v posledních třech letech. Podle zprávy pro americký úřad pro bezpečnost silničního provozu může dojít k selhání západky.</p>',
        'image_url': 'https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=1000',
        'image_caption': 'Tesla Model 3',
        'category_name': 'Technologie',
        'home_position': 0
    },
    {
        'title': 'Čeští hokejisté zahájili přípravu',
        'perex': 'Hokejová reprezentace zahájila přípravu na blížící se mistrovství světa. Trenér Radim Rulík přivítal na srazu první hráče.',
        'content': '<p>„Kluci přijeli s chutí, to je pro mě nejdůležitější. Máme před sebou měsíc tvrdé práce,“ řekl novinářům Rulík po prvním tréninku na ledě.</p>',
        'image_url': 'https://d15-a.sdn.cz/d_15/c_img_oZ_A/nsLxLojIBzXhfH1hDNv9NT/0670.jpeg',
        'image_caption': 'Trénink reprezentace',
        'category_name': 'Sport',
        'home_position': 0
    },
    {
        'title': 'Inflace klesá, hypotéky by mohly zlevnit',
        'perex': 'Inflace klesá rychleji, než se čekalo, a blíží se k cíli centrální banky. To dává naději na brzké snížení úrokových sazeb.',
        'content': '<p>Guvernér ČNB naznačil, že pokud bude tento trend pokračovat, bankovní rada by mohla přistoupit ke snížení základní úrokové sazby již na příštím zasedání.</p>',
        'image_url': 'https://images.unsplash.com/photo-1580519542036-c47de6196ba5?q=80&w=1000',
        'image_caption': 'Ilustrační foto',
        'category_name': 'Ekonomika',
        'home_position': 0
    },
    {
        'title': 'Nový iPhone překvapil výdrží',
        'perex': 'První testy nového iPhonu přinášejí překvapení. Díky úspornějšímu čipu vydrží telefon na jedno nabití o tři hodiny déle.',
        'content': '<p>Technologičtí novináři si pochvalují zejména optimalizaci systému iOS. I při náročném používání se telefon nepřehřívá.</p>',
        'image_url': 'https://images.unsplash.com/photo-1512054502232-10a0a035d672?q=80&w=1000',
        'image_caption': 'Nový model iPhone',
        'category_name': 'Technologie',
        'home_position': 0
    },
    {
        'title': 'Slavia v derby rozdrtila Spartu',
        'perex': 'Slavia ovládla 309. derby pražských „S“. V Edenu nedala Spartě šanci a zvítězila vysoko 4:0.',
        'content': '<p>Zápas začal ve vysokém tempu a Slavia šla do vedení už v 10. minutě po rohovém kopu. Sparta se snažila odpovědět, ale marně.</p>',
        'image_url': 'https://www.ruik.cz/wp-content/uploads/Tomas-Chory-Slavia-Praha-7.jpg',
        'image_caption': 'Radost hráčů Slavie',
        'category_name': 'Sport',
        'home_position': 0
    }
]

def reset_database():
    print("🧨 Mazání staré databáze...")
    # Cesta k DB souboru (o dvě úrovně výš)
    db_path = os.path.join(os.path.dirname(__file__), '../../news.db')
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            print("❌ CHYBA: Databázi někdo používá. Vypni server (Ctrl+C) a zkus to znovu!")
            return
    
    print("🏗️  Vytváření tabulek...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("👤 Vytváření uživatelů...")

    default_pw = hash_password("heslo123")
    
    users = [
        User(email="admin@zpravy.cz", name="Hlavní Admin", password_hash=default_pw, role=Role.ADMIN, is_active=True),
        User(email="sefredaktor@zpravy.cz", name="Karel Šéf", password_hash=default_pw, role=Role.CHIEF_EDITOR, is_active=True),
        User(email="redaktor@zpravy.cz", name="Jan Novák", password_hash=default_pw, role=Role.EDITOR, is_active=True),
        User(email="ctenar@zpravy.cz", name="Jiří Novotný", password_hash=default_pw, role=Role.READER, is_active=True),
        User(email="ctenar2@zpravy.cz", name="Petr Svoboda", password_hash=default_pw, role=Role.READER, is_active=True),
        User(email="franta@zpravy.cz", name="František Strašpytel", password_hash=default_pw, role=Role.READER, is_active=True)
    ]
    
    db.add_all(users)
    db.commit()
    
    redaktor = users[2] 
    
    print("📂 Vytváření kategorií...")
    categories = {}
    cat_names = set(a['category_name'] for a in articles_data)
    for name in cat_names:
        c = Category(name=name, description=f"Zprávy z rubriky {name}")
        db.add(c)
        categories[name] = c
    db.commit() 
    
    print(f"📰 Vytváření {len(articles_data)} článků...")
    now = datetime.now(timezone.utc)
    
    created_objects = []
    
    for i, data in enumerate(articles_data):
        cat = categories.get(data['category_name'])
        article_time = now - timedelta(hours=i*2) 
        
        last_promoted = article_time if data['home_position'] > 0 else None
        
        art = Article(
            title=data['title'],
            perex=data['perex'],
            content=data['content'],
            image_url=data['image_url'],
            image_caption=data.get('image_caption'),
            status=ArticleStatus.PUBLISHED,
            home_position=data['home_position'],
            last_promoted_at=last_promoted,
            author_id=redaktor.id,
            category_id=cat.id if cat else None,
            created_at=article_time,
            updated_at=article_time
        )
        created_objects.append(art)
        db.add(art)
    
    db.commit() 
    
    print("✅ HOTOVO! Databáze je obnovena.")
    print("ℹ️  Všichni uživatelé mají heslo: heslo123")
    db.close()

if __name__ == "__main__":
    reset_database()