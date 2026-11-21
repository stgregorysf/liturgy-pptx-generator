# liturgy-pptx-generator

install libraries
```sh
python3 -m venv .venv

source .venv/bin/activate

python -m pip install -r requirements.txt
```

usage

```sh
python generate_slides.py 2026-11-22
# add --nor_dzaghig at the end optionally
```

to generate a copy paste message to tell others about the liturgy variation:
```sh
# python generate_slides.py 2026-11-22 --whatsapp    
2026-11-21T12:32:07.951Z WARNING:root:daily readings url is https://dailyreadings.am/v3/getHourlyText.php?hdate=1515342&hour=3558
2026-11-21T12:32:09.200Z INFO:root:
Ասիկա այսօրուան Daily Worship-ի էջն է։
https://dailyreadings.am/v3/getHourlyText.php?hdate=1515342&hour=3558

Պօղոսի առաքելոյն ի Թեսաղոնիկեցւոց առաջին թղթոյն է ընթերցուածս

Ալէլուիա, ալէլուիա: Յարեաւ Աստուած, եւ ցրուեցան ամենայն թշնամիք Նորա, փախեան ատելիք Նորա յերեսաց Նորա:

Ղուկասու 12:13 - 12:31

Օրհնեալ, գովեալ եւ փառաւորեալ, հրաշալի եւ աստուածազարդ յարութեանն Քրիստոսի երկիր պագանեմք:
```


### getting verses from the bible
inside this project, the unicode folder should be formatted with two directories

within each directory is each book of the bible. in each "book" directory is txt files

the name of the txt file corresponds to the chapter of the book, like:
```
unicode/
├── armenian
│   ├── acts
│   │   ├── 1.txt
│   │   ├── 2.txt
│   │   └── ...
│   ├── ... all the other books
│   └── john
│       ├── 1.txt
│       └── ...
├── keep
└── nkjv
    ├── acts
    │   ├── 1.txt
    │   └── ...
    ├── ... all the other books
    └── john
        ├── 1.txt
        └── ...
```

each txt file should be formatted such that the line number on the file corresponds to the verse

so if you wanted john 3:16, you would go to unicode/armenian/john/3.txt and go to line 16

same for the nkjv folder
```
cat unicode/armenian/john/3.txt | head
verse 1
verse 2
```

### what generated slides look like
```py
VersePair(
    reading_code="",
    armenian_text="Նոր ծաղիկ պայծառ ցուցաւ, այսօր ի նոր գերեզմանէն:",
    transliterated_text=transliteration.transliterate("Նոր ծաղիկ պայծառ ցուցաւ, այսօր ի նոր գերեզմանէն:"),
    niv_text="New flower that shone bright, today from the new grave.",
),
VersePair(
    reading_code="",
    armenian_text="Երեւեալ լոյս յարութեան, աւետիս,",
    transliterated_text=transliteration.transliterate("Երեւեալ լոյս յարութեան, աւետիս,"),
    niv_text="Revealed light of the resurrection, Good News.",
),
VersePair(
    reading_code="",
    armenian_text="ի խաւարի ստուերաց մահու, աւետիս:",
    transliterated_text=transliteration.transliterate("ի խաւարի ստուերաց մահու, աւետիս:"),
    niv_text="In the darkness of the shadow of death, Good News.",
),
VersePair(
    reading_code="",
    armenian_text="Յարեաւ Քրիստոս, աւետիս:",
    transliterated_text=transliteration.transliterate("Յարեաւ Քրիստոս, աւետիս:"),
    niv_text="Christ has arisen, Good News.",
),
```

becomes

<img width="1701" height="987" alt="Screenshot 2026-11-21 at 2 23 29 PM" src="https://github.com/user-attachments/assets/520f734f-e3eb-4a26-a600-58bb0d954058" />
