import pygame
import math
import copy

pygame.init()

# =========================================================
# AKEN
# =========================================================

WIDTH = 1200
HEIGHT = 760

SIDEBAR_WIDTH = 310
CANVAS_WIDTH = WIDTH - SIDEBAR_WIDTH

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elektriskeemi koostaja")

clock = pygame.time.Clock()


# =========================================================
# VÄRVID
# =========================================================

VALGE = (255, 255, 255)
MUST = (26, 39, 48)

HALL = (238, 243, 245)
HELE_HALL = (248, 250, 251)

ROHELINE = (20, 166, 112)
HELE_ROHELINE = (220, 246, 235)

PUNANE = (205, 75, 72)
HELE_PUNANE = (255, 232, 229)

KOLLANE = (255, 220, 0)
HELE_KOLLANE = (255, 245, 80)

SININE = (50, 126, 171)
TUMEPANEEL = (26, 40, 49)
PANEELI_TEKS = (224, 235, 238)
PANEELI_VAIKNE = (150, 171, 179)
RUUDUSTIK = (229, 236, 239)


# =========================================================
# FONDID
# =========================================================

font = pygame.font.SysFont("segoeui", 22)
väike_font = pygame.font.SysFont("segoeui", 16)
pealkirja_font = pygame.font.SysFont("segoeui", 25, bold=True)
arvu_font = pygame.font.SysFont("segoeui", 29, bold=True)


# =========================================================
# SEADISTUSED
# =========================================================

RIBA_KÕRGUS = 72

DETAILI_LAIUS = 60
DETAILI_KÕRGUS = 40

JUHTME_PIKKUS = 90

ÜHENDUSE_KAUGUS = 25
KONTAKTI_KAUGUS = 14

ALLIKA_SISETAKISTUS = 0.5
LAMBIPIRNI_MIN_VOIMSUS = 0.025
LAMBIPIRNI_PLOKIMISPIIR = 1.5


# =========================================================
# ABIFUNKTSIOONID
# =========================================================

def kaugus(a, b):

    return math.hypot(
        a[0] - b[0],
        a[1] - b[1]
    )


def pööra_punkt(x, y, cx, cy, nurk):

    rad = math.radians(nurk)

    dx = x - cx
    dy = y - cy

    uus_x = (
        dx * math.cos(rad)
        -
        dy * math.sin(rad)
    )

    uus_y = (
        dx * math.sin(rad)
        +
        dy * math.cos(rad)
    )

    return (
        cx + uus_x,
        cy + uus_y
    )


def punkti_kaugus_lõigust(
    px,
    py,
    x1,
    y1,
    x2,
    y2
):

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:

        return math.hypot(
            px - x1,
            py - y1
        )

    t = (
        (px - x1) * dx
        +
        (py - y1) * dy
    ) / (
        dx * dx
        +
        dy * dy
    )

    t = max(
        0,
        min(1, t)
    )

    lähim_x = x1 + t * dx
    lähim_y = y1 + t * dy

    return math.hypot(
        px - lähim_x,
        py - lähim_y
    )


# =========================================================
# DETAIL
# =========================================================

class Detail:

    def __init__(
        self,
        tüüp,
        x,
        y
    ):

        self.tüüp = tüüp

        self.x = x
        self.y = y

        self.nurk = 0
        self.takistus = 100.0
        self.pinge = 9.0
        self.nominaalvõimsus = 0.25
        self.läbi_põlenud = False

        if tüüp == "lamp":
            self.takistus = 20.0


        # -------------------------------------------------
        # JUHE
        # -------------------------------------------------

        if tüüp == "juhe":

            self.algus_x = x - JUHTME_PIKKUS / 2
            self.algus_y = y

            self.lõpp_x = x + JUHTME_PIKKUS / 2
            self.lõpp_y = y


    # =====================================================
    # JUHTME KESKPUNKT
    # =====================================================

    def uuenda_keskpunkt(self):

        if self.tüüp != "juhe":
            return

        self.x = (
            self.algus_x +
            self.lõpp_x
        ) / 2

        self.y = (
            self.algus_y +
            self.lõpp_y
        ) / 2


    # =====================================================
    # DETAILI KONTAKTID
    # =====================================================

    def kontaktid(self):

        # JUHE

        if self.tüüp == "juhe":

            return [
                (
                    self.algus_x,
                    self.algus_y
                ),
                (
                    self.lõpp_x,
                    self.lõpp_y
                )
            ]


        # MUU DETAIL

        kaugus_keskelt = DETAILI_LAIUS / 2 + 8

        rad = math.radians(
            self.nurk
        )

        dx = math.cos(rad) * kaugus_keskelt
        dy = math.sin(rad) * kaugus_keskelt

        return [
            (
                self.x - dx,
                self.y - dy
            ),
            (
                self.x + dx,
                self.y + dy
            )
        ]


    # =====================================================
    # RECT
    # =====================================================

    def rect(self):

        if self.tüüp == "juhe":

            min_x = min(
                self.algus_x,
                self.lõpp_x
            )

            max_x = max(
                self.algus_x,
                self.lõpp_x
            )

            min_y = min(
                self.algus_y,
                self.lõpp_y
            )

            max_y = max(
                self.algus_y,
                self.lõpp_y
            )

            return pygame.Rect(
                min_x - 10,
                min_y - 10,
                max_x - min_x + 20,
                max_y - min_y + 20
            )

        return pygame.Rect(
            self.x - 35,
            self.y - 35,
            70,
            70
        )


    # =====================================================
    # KAS HIIR ON DETAILIL
    # =====================================================

    def sisaldab(self, pos):

        mx, my = pos


        # JUHE

        if self.tüüp == "juhe":

            return (
                punkti_kaugus_lõigust(
                    mx,
                    my,
                    self.algus_x,
                    self.algus_y,
                    self.lõpp_x,
                    self.lõpp_y
                )
                <= 10
            )


        # LAMP

        if self.tüüp == "lamp":

            return (
                math.hypot(
                    mx - self.x,
                    my - self.y
                )
                <= 24
            )


        # MUU DETAIL

        return self.rect().collidepoint(
            pos
        )


    # =====================================================
    # JOONISTAMINE
    # =====================================================

    def joonista(
        self,
        pind,
        valitud=False,
        lamp_põleb=False,
        lamp_läbi_põlenud=False
    ):

        kontaktid = self.kontaktid()


        # =================================================
        # JUHE
        # =================================================

        if self.tüüp == "juhe":

            pygame.draw.line(
                pind,
                MUST,
                kontaktid[0],
                kontaktid[1],
                5
            )

            pygame.draw.circle(
                pind,
                MUST,
                (
                    int(kontaktid[0][0]),
                    int(kontaktid[0][1])
                ),
                3
            )

            pygame.draw.circle(
                pind,
                MUST,
                (
                    int(kontaktid[1][0]),
                    int(kontaktid[1][1])
                ),
                3
            )


            if valitud:

                pygame.draw.circle(
                    pind,
                    ROHELINE,
                    (
                        int(kontaktid[0][0]),
                        int(kontaktid[0][1])
                    ),
                    9,
                    2
                )

                pygame.draw.circle(
                    pind,
                    ROHELINE,
                    (
                        int(kontaktid[1][0]),
                        int(kontaktid[1][1])
                    ),
                    9,
                    2
                )

            return


        # =================================================
        # DETAILI JUHTMED
        # =================================================

        vasak_keha = pööra_punkt(
            self.x - DETAILI_LAIUS / 2,
            self.y,
            self.x,
            self.y,
            self.nurk
        )

        parem_keha = pööra_punkt(
            self.x + DETAILI_LAIUS / 2,
            self.y,
            self.x,
            self.y,
            self.nurk
        )


        pygame.draw.line(
            pind,
            MUST,
            kontaktid[0],
            vasak_keha,
            3
        )

        pygame.draw.line(
            pind,
            MUST,
            parem_keha,
            kontaktid[1],
            3
        )


        # =================================================
        # TAKISTI
        # =================================================

        if self.tüüp == "takisti":

            punktid = []

            for px, py in [
                (-30, -18),
                (30, -18),
                (30, 18),
                (-30, 18)
            ]:

                punktid.append(
                    pööra_punkt(
                        self.x + px,
                        self.y + py,
                        self.x,
                        self.y,
                        self.nurk
                    )
                )


            pygame.draw.polygon(
                pind,
                VALGE,
                punktid
            )

            pygame.draw.polygon(
                pind,
                MUST,
                punktid,
                2
            )


            tekst = font.render(
                "R",
                True,
                MUST
            )

            tekst = pygame.transform.rotate(
                tekst,
                -self.nurk
            )


            pind.blit(
                tekst,
                (
                    self.x -
                    tekst.get_width() / 2,

                    self.y -
                    tekst.get_height() / 2
                )
            )

            väärtuse_tekst = väike_font.render(
                f"{self.takistus:g} Ω",
                True,
                MUST
            )

            pind.blit(
                väärtuse_tekst,
                (
                    self.x - väärtuse_tekst.get_width() / 2,
                    self.y + 23
                )
            )


        # =================================================
        # LAMP
        # =================================================

        elif self.tüüp == "lamp":

            if lamp_läbi_põlenud:

                värv = (188, 193, 194)

            elif lamp_põleb:

                värv = HELE_KOLLANE

            else:

                värv = VALGE


            pygame.draw.circle(
                pind,
                värv,
                (
                    int(self.x),
                    int(self.y)
                ),
                18
            )

            pygame.draw.circle(
                pind,
                MUST,
                (
                    int(self.x),
                    int(self.y)
                ),
                18,
                2
            )


            if lamp_läbi_põlenud:

                pygame.draw.line(
                    pind,
                    PUNANE,
                    (self.x - 10, self.y - 10),
                    (self.x + 10, self.y + 10),
                    3
                )

                pygame.draw.line(
                    pind,
                    PUNANE,
                    (self.x + 10, self.y - 10),
                    (self.x - 10, self.y + 10),
                    3
                )


            rad = math.radians(
                self.nurk
            )

            dx = math.cos(rad) * 11
            dy = math.sin(rad) * 11

            px = -math.sin(rad) * 11
            py = math.cos(rad) * 11


            pygame.draw.line(
                pind,
                MUST,
                (
                    self.x - dx,
                    self.y - dy
                ),
                (
                    self.x + dx,
                    self.y + dy
                ),
                2
            )

            väärtuse_tekst = väike_font.render(
                f"{self.takistus:g} Ω",
                True,
                MUST
            )

            pind.blit(
                väärtuse_tekst,
                (
                    self.x - väärtuse_tekst.get_width() / 2,
                    self.y + 23
                )
            )

            pygame.draw.line(
                pind,
                MUST,
                (
                    self.x - px,
                    self.y - py
                ),
                (
                    self.x + px,
                    self.y + py
                ),
                2
            )


        # =================================================
        # VOOLUALLIKAS
        # =================================================

        elif self.tüüp == "vooluallikas":

            punktid = []

            for px, py in [
                (-30, -20),
                (30, -20),
                (30, 20),
                (-30, 20)
            ]:

                punktid.append(
                    pööra_punkt(
                        self.x + px,
                        self.y + py,
                        self.x,
                        self.y,
                        self.nurk
                    )
                )


            pygame.draw.polygon(
                pind,
                VALGE,
                punktid
            )

            pygame.draw.polygon(
                pind,
                MUST,
                punktid,
                2
            )


            # MIINUS

            p1 = pööra_punkt(
                self.x - 18,
                self.y,
                self.x,
                self.y,
                self.nurk
            )

            p2 = pööra_punkt(
                self.x - 7,
                self.y,
                self.x,
                self.y,
                self.nurk
            )


            pygame.draw.line(
                pind,
                MUST,
                p1,
                p2,
                3
            )

            väärtuse_tekst = väike_font.render(
                f"{self.pinge:g} V",
                True,
                MUST
            )

            pind.blit(
                väärtuse_tekst,
                (
                    self.x - väärtuse_tekst.get_width() / 2,
                    self.y + 22
                )
            )


            # PLUSS

            p1 = pööra_punkt(
                self.x + 7,
                self.y,
                self.x,
                self.y,
                self.nurk
            )

            p2 = pööra_punkt(
                self.x + 18,
                self.y,
                self.x,
                self.y,
                self.nurk
            )


            pygame.draw.line(
                pind,
                MUST,
                p1,
                p2,
                3
            )


            p1 = pööra_punkt(
                self.x + 12,
                self.y - 5,
                self.x,
                self.y,
                self.nurk
            )

            p2 = pööra_punkt(
                self.x + 12,
                self.y + 5,
                self.x,
                self.y,
                self.nurk
            )


            pygame.draw.line(
                pind,
                MUST,
                p1,
                p2,
                3
            )


        # =================================================
        # VALIK
        # =================================================

        if valitud:

            if self.tüüp == "lamp":

                pygame.draw.circle(
                    pind,
                    ROHELINE,
                    (
                        int(self.x),
                        int(self.y)
                    ),
                    26,
                    2
                )

            else:

                pygame.draw.rect(
                    pind,
                    ROHELINE,
                    self.rect().inflate(
                        8,
                        8
                    ),
                    2
                )


# =========================================================
# DETAILI OTSIMINE
# =========================================================

def leia_detail(pos):

    for detail in reversed(detailid):

        if detail.sisaldab(pos):

            return detail

    return None


# =========================================================
# LÄHIMA KONTAKTI OTSIMINE
# =========================================================

def leia_lähim_kontakt(
    punkt,
    välja_arvatud=None
):

    parim = None
    parim_kaugus = ÜHENDUSE_KAUGUS

    for detail in detailid:

        if detail is välja_arvatud:
            continue


        for kontakt in detail.kontaktid():

            d = kaugus(
                punkt,
                kontakt
            )


            if d < parim_kaugus:

                parim_kaugus = d
                parim = kontakt


    return parim


# =========================================================
# DETAILI ÜHENDAMINE
# =========================================================

def ühenda_detail(detail):

    if detail not in detailid:
        return


    parim_nihutus = None
    väikseim_kaugus = ÜHENDUSE_KAUGUS


    for kontakt in detail.kontaktid():

        siht = leia_lähim_kontakt(
            kontakt,
            detail
        )


        if siht is None:
            continue


        d = kaugus(
            kontakt,
            siht
        )


        if d < väikseim_kaugus:

            väikseim_kaugus = d

            parim_nihutus = (
                siht[0] - kontakt[0],
                siht[1] - kontakt[1]
            )


    if parim_nihutus is None:
        return


    dx, dy = parim_nihutus


    # JUHE

    if detail.tüüp == "juhe":

        detail.algus_x += dx
        detail.algus_y += dy

        detail.lõpp_x += dx
        detail.lõpp_y += dy

        detail.uuenda_keskpunkt()


    # MUU DETAIL

    else:

        detail.x += dx
        detail.y += dy


# =========================================================
# JUHTME ÜHE OTSA ÜHENDAMINE
# =========================================================

def ühenda_juhtme_ots(
    detail,
    ots
):

    if detail.tüüp != "juhe":
        return


    if ots == "algus":

        punkt = (
            detail.algus_x,
            detail.algus_y
        )

    else:

        punkt = (
            detail.lõpp_x,
            detail.lõpp_y
        )


    siht = leia_lähim_kontakt(
        punkt,
        detail
    )


    if siht is None:
        return


    if kaugus(
        punkt,
        siht
    ) > ÜHENDUSE_KAUGUS:

        return


    if ots == "algus":

        detail.algus_x = siht[0]
        detail.algus_y = siht[1]

    else:

        detail.lõpp_x = siht[0]
        detail.lõpp_y = siht[1]


    detail.uuenda_keskpunkt()


# =========================================================
# AHELA ARVUTAMINE
# =========================================================

def lahenda_võrrandisüsteem(maatriks, tulemused):

    suurus = len(tulemused)

    for veerg in range(suurus):

        pivot = max(
            range(veerg, suurus),
            key=lambda rida: abs(maatriks[rida][veerg])
        )

        if abs(maatriks[pivot][veerg]) < 1e-12:
            return None

        maatriks[veerg], maatriks[pivot] = maatriks[pivot], maatriks[veerg]
        tulemused[veerg], tulemused[pivot] = tulemused[pivot], tulemused[veerg]

        jagaja = maatriks[veerg][veerg]

        for kirje in range(veerg, suurus):
            maatriks[veerg][kirje] /= jagaja

        tulemused[veerg] /= jagaja

        for rida in range(veerg + 1, suurus):

            kordaja = maatriks[rida][veerg]

            if kordaja == 0:
                continue

            for kirje in range(veerg, suurus):
                maatriks[rida][kirje] -= kordaja * maatriks[veerg][kirje]

            tulemused[rida] -= kordaja * tulemused[veerg]

    vastus = [0.0] * suurus

    for rida in range(suurus - 1, -1, -1):

        vastus[rida] = tulemused[rida] - sum(
            maatriks[rida][veerg] * vastus[veerg]
            for veerg in range(rida + 1, suurus)
        )

    return vastus


def lahenda_ahel(allikas):

    kontaktide_arv = len(detailid) * 2
    vanem = list(range(kontaktide_arv))

    def leia(indeks):

        while vanem[indeks] != indeks:
            vanem[indeks] = vanem[vanem[indeks]]
            indeks = vanem[indeks]

        return indeks

    def ühenda(a, b):

        juur_a = leia(a)
        juur_b = leia(b)

        if juur_a != juur_b:
            vanem[juur_b] = juur_a

    kontaktipunktid = [
        kontakt
        for detail in detailid
        for kontakt in detail.kontaktid()
    ]

    for i, punkt_a in enumerate(kontaktipunktid):

        for j in range(i + 1, kontaktide_arv):

            punkt_b = kontaktipunktid[j]

            if (
                (punkt_a[0] - punkt_b[0]) ** 2
                + (punkt_a[1] - punkt_b[1]) ** 2
                <= 16
            ):

                ühenda(i, j)

    for indeks, detail in enumerate(detailid):

        if detail.tüüp == "juhe":
            ühenda(indeks * 2, indeks * 2 + 1)

    allika_indeks = detailid.index(allikas) * 2
    maandus = leia(allika_indeks)
    positiivne = leia(allika_indeks + 1)

    takistid = []

    for indeks, detail in enumerate(detailid):

        if detail.tüüp not in ("takisti", "lamp"):
            continue

        if detail.tüüp == "lamp" and detail.läbi_põlenud:
            continue

        if detail.takistus <= 0:
            continue

        takistid.append(
            (
                leia(indeks * 2),
                leia(indeks * 2 + 1),
                detail.takistus,
                detail
            )
        )

    ühendused = {}

    for a, b, _, detail in takistid:

        if a == b:
            continue

        ühendused.setdefault(a, []).append((b, detail))
        ühendused.setdefault(b, []).append((a, detail))

    nähtud = {positiivne}
    järjekord = [positiivne]

    while järjekord:

        praegune = järjekord.pop()

        for järgmine, _ in ühendused.get(praegune, ()):

            if järgmine not in nähtud:
                nähtud.add(järgmine)
                järjekord.append(järgmine)

    suletud = maandus in nähtud

    if not suletud:

        return {
            "suletud": False,
            "lühis": False,
            "pinge": allikas.pinge,
            "takistus": math.inf,
            "vool": 0.0,
            "lambi_võimsused": {},
        }

    if positiivne == maandus:

        return {
            "suletud": True,
            "lühis": True,
            "pinge": 0.0,
            "takistus": 0.0,
            "vool": allikas.pinge / ALLIKA_SISETAKISTUS,
            "lambi_võimsused": {
                detail: 0.0
                for detail in detailid
                if detail.tüüp == "lamp"
            },
        }

    tundmatud = [sõlm for sõlm in nähtud if sõlm != maandus]
    indeksid = {sõlm: indeks for indeks, sõlm in enumerate(tundmatud)}
    maatriks = [
        [0.0] * len(tundmatud)
        for _ in tundmatud
    ]
    tulemused = [0.0] * len(tundmatud)

    def lisa_takisti(sõlm_a, sõlm_b, takistus, fikseeritud_pinge=0.0):

        juhtivus = 1.0 / takistus
        indeks_a = indeksid.get(sõlm_a)
        indeks_b = indeksid.get(sõlm_b)

        if indeks_a is not None:
            maatriks[indeks_a][indeks_a] += juhtivus

            if indeks_b is not None:
                maatriks[indeks_a][indeks_b] -= juhtivus
            else:
                tulemused[indeks_a] += juhtivus * fikseeritud_pinge

        if indeks_b is not None:
            maatriks[indeks_b][indeks_b] += juhtivus

            if indeks_a is not None:
                maatriks[indeks_b][indeks_a] -= juhtivus
            else:
                tulemused[indeks_b] += juhtivus * fikseeritud_pinge

    for a, b, takistus, _ in takistid:

        if a in nähtud and b in nähtud:
            lisa_takisti(a, b, takistus)

    lisa_takisti(
        positiivne,
        None,
        ALLIKA_SISETAKISTUS,
        allikas.pinge
    )

    pinged = lahenda_võrrandisüsteem(maatriks, tulemused)

    if pinged is None:

        return {
            "suletud": False,
            "lühis": False,
            "pinge": allikas.pinge,
            "takistus": math.inf,
            "vool": 0.0,
            "lambi_võimsused": {},
        }

    sõlme_pinged = {maandus: 0.0}
    sõlme_pinged.update(
        (sõlm, pinged[indeks])
        for sõlm, indeks in indeksid.items()
    )

    lambi_võimsused = {}

    for a, b, takistus, detail in takistid:

        if detail.tüüp == "lamp":

            pinge = sõlme_pinged.get(a, 0.0) - sõlme_pinged.get(b, 0.0)
            lambi_võimsused[detail] = pinge * pinge / takistus

    klemmipinge = max(0.0, sõlme_pinged.get(positiivne, 0.0))
    vool = max(0.0, (allikas.pinge - klemmipinge) / ALLIKA_SISETAKISTUS)
    ekvivalenttakistus = (
        klemmipinge / vool
        if vool > 1e-12
        else math.inf
    )

    return {
        "suletud": True,
        "lühis": False,
        "pinge": klemmipinge,
        "takistus": ekvivalenttakistus,
        "vool": vool,
        "lambi_võimsused": lambi_võimsused,
    }


def simuleeri_ahel():

    allikad = [
        detail
        for detail in detailid
        if detail.tüüp == "vooluallikas"
    ]
    lambid = [
        detail
        for detail in detailid
        if detail.tüüp == "lamp"
    ]

    if not allikad:

        tulemus = {
            "suletud": False,
            "lühis": False,
            "pinge": 0.0,
            "takistus": math.inf,
            "vool": 0.0,
            "lambi_võimsused": {},
        }

    else:

        while True:

            tulemus = lahenda_ahel(allikad[0])

            plahvatanud = [
                lamp
                for lamp in lambid
                if (
                    not lamp.läbi_põlenud
                    and tulemus["lambi_võimsused"].get(lamp, 0.0)
                    > lamp.nominaalvõimsus * LAMBIPIRNI_PLOKIMISPIIR
                )
            ]

            if not plahvatanud:
                break

            for lamp in plahvatanud:
                lamp.läbi_põlenud = True

    lambi_võimsus = max(
        tulemus["lambi_võimsused"].values(),
        default=0.0
    )

    tulemus["lambi_võimsus"] = lambi_võimsus
    tulemus["lambid_läbi"] = any(lamp.läbi_põlenud for lamp in lambid)
    tulemus["lambid_põlevad"] = {
        lamp: (
            not lamp.läbi_põlenud
            and tulemus["lambi_võimsused"].get(lamp, 0.0)
            >= LAMBIPIRNI_MIN_VOIMSUS
        )
        for lamp in lambid
    }
    tulemus["lamp_põleb"] = any(tulemus["lambid_põlevad"].values())

    return tulemus


# =========================================================
# AJALUGU
# =========================================================

ajalugu = []


def salvesta():

    ajalugu.append(
        copy.deepcopy(
            detailid
        )
    )


    if len(ajalugu) > 50:

        ajalugu.pop(0)


def tagasi():

    global detailid
    global valitud_detail

    if not ajalugu:
        return


    detailid = ajalugu.pop()

    valitud_detail = None


# =========================================================
# NUPUD
# =========================================================

nupud = [

    (
        "takisti",
        pygame.Rect(
            14,
            14,
            108,
            44
        ),
        "Takisti"
    ),

    (
        "lamp",
        pygame.Rect(
            130,
            14,
            96,
            44
        ),
        "Lamp"
    ),

    (
        "vooluallikas",
        pygame.Rect(
            234,
            14,
            146,
            44
        ),
        "Vooluallikas"
    ),

    (
        "juhe",
        pygame.Rect(
            388,
            14,
            92,
            44
        ),
        "Juhe"
    )
]


kustuta_nupp = pygame.Rect(
    488,
    14,
    98,
    44
)

tagasi_nupp = pygame.Rect(
    594,
    14,
    94,
    44
)

omaduse_väli = pygame.Rect(
    CANVAS_WIDTH + 22,
    468,
    SIDEBAR_WIDTH - 44,
    46
)


# =========================================================
# MUUTUJAD
# =========================================================

detailid = []

valitud_tüüp = None

valitud_detail = None

# Detail, mis on hetkel hiirega kaasas.

käes_olev = None

# Juba laual oleva detaili liigutamine.

lohistatav = None

lohistamise_tüüp = None

nihke_x = 0
nihke_y = 0

muudetav_väli = None
välja_tekst = ""
sisendi_viga = False
asenda_väli = False
simulatsioon_vajab_uuendust = True
simulatsiooni_tulemus = None


# =========================================================
# PEAMINE TSÜKKEL
# =========================================================

töötab = True


while töötab:

    # =====================================================
    # SÜNDMUSED
    # =====================================================

    for event in pygame.event.get():

        if event.type in (
            pygame.KEYDOWN,
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION
        ):

            simulatsioon_vajab_uuendust = True

        # =================================================
        # SULGEMINE
        # =================================================

        if event.type == pygame.QUIT:

            töötab = False


        # =================================================
        # KLAVIATUUR
        # =================================================

        elif event.type == pygame.KEYDOWN:

            if muudetav_väli is not None:

                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):

                    try:

                        uus_väärtus = float(
                            välja_tekst.replace(",", ".")
                        )

                    except ValueError:

                        uus_väärtus = 0


                    if (
                        math.isfinite(uus_väärtus)
                        and uus_väärtus > 0
                        and valitud_detail is not None
                    ):

                        salvesta()

                        if muudetav_väli == "takistus":

                            valitud_detail.takistus = uus_väärtus

                        else:

                            valitud_detail.pinge = uus_väärtus


                        muudetav_väli = None
                        sisendi_viga = False

                    else:

                        sisendi_viga = True
                        asenda_väli = True


                elif event.key == pygame.K_BACKSPACE:

                    if asenda_väli:

                        välja_tekst = ""

                    else:

                        välja_tekst = välja_tekst[:-1]

                    asenda_väli = False
                    sisendi_viga = False


                elif event.key == pygame.K_ESCAPE:

                    muudetav_väli = None
                    sisendi_viga = False


                elif event.unicode in "0123456789.," and len(välja_tekst) < 14:

                    if asenda_väli:

                        välja_tekst = event.unicode

                    else:

                        välja_tekst += event.unicode

                    asenda_väli = False
                    sisendi_viga = False


            elif (
                event.key == pygame.K_z
                and
                event.mod & pygame.KMOD_CTRL
            ):

                tagasi()


        # =================================================
        # HIIRE NUPP ALLA
        # =================================================

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = pygame.mouse.get_pos()


            # =================================================
            # VASAK HIIRE NUPP
            # =================================================

            if event.button == 1:

                nuppudele_vajutus = False
                muudetav_väli = None


                if mx >= CANVAS_WIDTH:

                    nuppudele_vajutus = True

                    if (
                        omaduse_väli.collidepoint(mx, my)
                        and valitud_detail is not None
                        and valitud_detail.tüüp in ("takisti", "lamp", "vooluallikas")
                    ):

                        if valitud_detail.tüüp in ("takisti", "lamp"):

                            muudetav_väli = "takistus"
                            välja_tekst = f"{valitud_detail.takistus:g}"

                        else:

                            muudetav_väli = "pinge"
                            välja_tekst = f"{valitud_detail.pinge:g}"

                        asenda_väli = True
                        sisendi_viga = False


                # =================================================
                # DETAILI NUPUD
                # =================================================

                for tüüp, rect, nimi in nupud:

                    if rect.collidepoint(
                        mx,
                        my
                    ):

                        nuppudele_vajutus = True


                        # Sama nupp = tühista valik.

                        if valitud_tüüp == tüüp:

                            valitud_tüüp = None
                            käes_olev = None

                        else:

                            valitud_tüüp = tüüp

                            käes_olev = Detail(
                                tüüp,
                                mx,
                                my
                            )


                        valitud_detail = None

                        break


                # =================================================
                # KUSTUTA
                # =================================================

                if kustuta_nupp.collidepoint(
                    mx,
                    my
                ):

                    nuppudele_vajutus = True


                    if valitud_detail is not None:

                        salvesta()


                        if valitud_detail in detailid:

                            detailid.remove(
                                valitud_detail
                            )


                        valitud_detail = None


                if tagasi_nupp.collidepoint(mx, my):

                    nuppudele_vajutus = True
                    tagasi()


                # =================================================
                # TÖÖALA
                # =================================================

                if not nuppudele_vajutus:

                    # =============================================
                    # DETAIL ON KÄES
                    # =============================================

                    if käes_olev is not None:

                        if my > RIBA_KÕRGUS and mx < CANVAS_WIDTH:

                            salvesta()


                            uus = copy.deepcopy(
                                käes_olev
                            )


                            detailid.append(
                                uus
                            )


                            ühenda_detail(
                                uus
                            )


                            valitud_detail = uus


                            # -------------------------------------
                            # Uus sama tüüpi detail jääb kätte.
                            # -------------------------------------

                            käes_olev = Detail(
                                valitud_tüüp,
                                mx,
                                my
                            )


                    # =============================================
                    # MIDAGI EI OLE KÄES
                    # =============================================

                    else:

                        detail = leia_detail(
                            (
                                mx,
                                my
                            )
                        )


                        valitud_detail = detail


                        if detail is not None:

                            lohistatav = detail


                            # =====================================
                            # JUHE
                            # =====================================

                            if detail.tüüp == "juhe":

                                kaugus_algus = kaugus(
                                    (
                                        mx,
                                        my
                                    ),
                                    (
                                        detail.algus_x,
                                        detail.algus_y
                                    )
                                )


                                kaugus_lõpp = kaugus(
                                    (
                                        mx,
                                        my
                                    ),
                                    (
                                        detail.lõpp_x,
                                        detail.lõpp_y
                                    )
                                )


                                if (
                                    kaugus_algus
                                    <=
                                    KONTAKTI_KAUGUS
                                ):

                                    lohistamise_tüüp = (
                                        "algus"
                                    )


                                elif (
                                    kaugus_lõpp
                                    <=
                                    KONTAKTI_KAUGUS
                                ):

                                    lohistamise_tüüp = (
                                        "lõpp"
                                    )


                                else:

                                    lohistamise_tüüp = (
                                        "kogu"
                                    )


                                    nihke_x = (
                                        detail.x
                                        -
                                        mx
                                    )


                                    nihke_y = (
                                        detail.y
                                        -
                                        my
                                    )


                            # =====================================
                            # MUU DETAIL
                            # =====================================

                            else:

                                lohistamise_tüüp = (
                                    "kogu"
                                )


                                nihke_x = (
                                    detail.x
                                    -
                                    mx
                                )


                                nihke_y = (
                                    detail.y
                                    -
                                    my
                                )


            # =================================================
            # PAREM HIIRE NUPP
            # =================================================

            elif event.button == 3:

                # =============================================
                # JUHE / DETAIL ON KÄES
                # =============================================

                if käes_olev is not None:

                    # -----------------------------------------
                    # JUHTME PÖÖRAMINE
                    # -----------------------------------------

                    if käes_olev.tüüp == "juhe":

                        cx = käes_olev.x
                        cy = käes_olev.y


                        uus_algus = pööra_punkt(
                            käes_olev.algus_x,
                            käes_olev.algus_y,
                            cx,
                            cy,
                            90
                        )


                        uus_lõpp = pööra_punkt(
                            käes_olev.lõpp_x,
                            käes_olev.lõpp_y,
                            cx,
                            cy,
                            90
                        )


                        käes_olev.algus_x = (
                            uus_algus[0]
                        )

                        käes_olev.algus_y = (
                            uus_algus[1]
                        )


                        käes_olev.lõpp_x = (
                            uus_lõpp[0]
                        )

                        käes_olev.lõpp_y = (
                            uus_lõpp[1]
                        )


                        käes_olev.uuenda_keskpunkt()


                    # -----------------------------------------
                    # MUU DETAIL
                    # -----------------------------------------

                    else:

                        käes_olev.nurk += 90

                        if käes_olev.nurk >= 360:

                            käes_olev.nurk = 0


                # =============================================
                # LAUAL OLEV DETAIL
                # =============================================

                elif valitud_detail is not None:

                    salvesta()


                    detail = valitud_detail


                    # -----------------------------------------
                    # JUHE
                    # -----------------------------------------

                    if detail.tüüp == "juhe":

                        cx = detail.x
                        cy = detail.y


                        uus_algus = pööra_punkt(
                            detail.algus_x,
                            detail.algus_y,
                            cx,
                            cy,
                            90
                        )


                        uus_lõpp = pööra_punkt(
                            detail.lõpp_x,
                            detail.lõpp_y,
                            cx,
                            cy,
                            90
                        )


                        detail.algus_x = (
                            uus_algus[0]
                        )

                        detail.algus_y = (
                            uus_algus[1]
                        )


                        detail.lõpp_x = (
                            uus_lõpp[0]
                        )

                        detail.lõpp_y = (
                            uus_lõpp[1]
                        )


                        detail.uuenda_keskpunkt()


                    # -----------------------------------------
                    # MUU DETAIL
                    # -----------------------------------------

                    else:

                        detail.nurk += 90

                        if detail.nurk >= 360:

                            detail.nurk = 0


                    ühenda_detail(
                        detail
                    )


        # =====================================================
        # HIIRE LIIKUMINE
        # =====================================================

        elif event.type == pygame.MOUSEMOTION:

            mx, my = pygame.mouse.get_pos()


            # =================================================
            # DETAIL ON KÄES
            # =================================================

            if käes_olev is not None:

                # ---------------------------------------------
                # JUHE
                # ---------------------------------------------

                if käes_olev.tüüp == "juhe":

                    # Väga oluline:
                    # liigume mõlemat juhet korraga.
                    #
                    # See parandab vea, kus ainult x/y
                    # muutus, aga juhtme otsad jäid vanale
                    # kohale.

                    dx = (
                        mx
                        -
                        käes_olev.x
                    )

                    dy = (
                        my
                        -
                        käes_olev.y
                    )


                    käes_olev.algus_x += dx
                    käes_olev.algus_y += dy

                    käes_olev.lõpp_x += dx
                    käes_olev.lõpp_y += dy


                    käes_olev.uuenda_keskpunkt()


                # ---------------------------------------------
                # MUU DETAIL
                # ---------------------------------------------

                else:

                    käes_olev.x = mx
                    käes_olev.y = my


                # =================================================
                # MAGNEETILINE ÜHENDAMINE
                # =================================================

                lähim_kontakt = None
                lähim_siht = None

                väikseim_kaugus = (
                    ÜHENDUSE_KAUGUS
                )


                for kontakt in käes_olev.kontaktid():

                    siht = leia_lähim_kontakt(
                        kontakt,
                        käes_olev
                    )


                    if siht is None:
                        continue


                    d = kaugus(
                        kontakt,
                        siht
                    )


                    if d < väikseim_kaugus:

                        väikseim_kaugus = d

                        lähim_kontakt = kontakt

                        lähim_siht = siht


                if (
                    lähim_kontakt is not None
                    and
                    lähim_siht is not None
                ):

                    dx = (
                        lähim_siht[0]
                        -
                        lähim_kontakt[0]
                    )

                    dy = (
                        lähim_siht[1]
                        -
                        lähim_kontakt[1]
                    )


                    # -----------------------------------------
                    # Nihutame kogu detaili.
                    # -----------------------------------------

                    if käes_olev.tüüp == "juhe":

                        käes_olev.algus_x += dx
                        käes_olev.algus_y += dy

                        käes_olev.lõpp_x += dx
                        käes_olev.lõpp_y += dy

                        käes_olev.uuenda_keskpunkt()


                    else:

                        käes_olev.x += dx
                        käes_olev.y += dy


            # =================================================
            # LAUAL OLEV DETAIL
            # =================================================

            if lohistatav is not None:

                detail = lohistatav


                # =============================================
                # JUHE
                # =============================================

                if detail.tüüp == "juhe":

                    # -----------------------------------------
                    # KOGU JUHE
                    # -----------------------------------------

                    if lohistamise_tüüp == "kogu":

                        uus_kesk_x = (
                            mx
                            +
                            nihke_x
                        )

                        uus_kesk_y = (
                            my
                            +
                            nihke_y
                        )


                        dx = (
                            uus_kesk_x
                            -
                            detail.x
                        )

                        dy = (
                            uus_kesk_y
                            -
                            detail.y
                        )


                        detail.algus_x += dx
                        detail.algus_y += dy

                        detail.lõpp_x += dx
                        detail.lõpp_y += dy


                        detail.uuenda_keskpunkt()


                    # -----------------------------------------
                    # ALGUS
                    # -----------------------------------------

                    elif lohistamise_tüüp == "algus":

                        detail.algus_x = mx
                        detail.algus_y = my

                        detail.uuenda_keskpunkt()


                    # -----------------------------------------
                    # LÕPP
                    # -----------------------------------------

                    elif lohistamise_tüüp == "lõpp":

                        detail.lõpp_x = mx
                        detail.lõpp_y = my

                        detail.uuenda_keskpunkt()


                # =============================================
                # MUU DETAIL
                # =============================================

                else:

                    detail.x = (
                        mx
                        +
                        nihke_x
                    )

                    detail.y = (
                        my
                        +
                        nihke_y
                    )


        # =====================================================
        # HIIRE NUPP ÜLES
        # =====================================================

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:

                # =============================================
                # LAUALT LIIGUTATUD DETAIL
                # =============================================

                if lohistatav is not None:

                    detail = lohistatav


                    if detail.tüüp == "juhe":

                        if (
                            lohistamise_tüüp
                            ==
                            "algus"
                        ):

                            ühenda_juhtme_ots(
                                detail,
                                "algus"
                            )


                        elif (
                            lohistamise_tüüp
                            ==
                            "lõpp"
                        ):

                            ühenda_juhtme_ots(
                                detail,
                                "lõpp"
                            )


                        else:

                            ühenda_detail(
                                detail
                            )


                    else:

                        ühenda_detail(
                            detail
                        )


                lohistatav = None
                lohistamise_tüüp = None


    # =========================================================
    # AHELA SIMULATSIOON
    # =========================================================

    if simulatsioon_vajab_uuendust:

        simulatsiooni_tulemus = simuleeri_ahel()
        simulatsioon_vajab_uuendust = False


    lamp_põleb = simulatsiooni_tulemus["lamp_põleb"]
    lamp_läbi_põlenud = simulatsiooni_tulemus["lambid_läbi"]


    # =========================================================
    # TAUST
    # =========================================================

    screen.fill(
        HELE_HALL
    )


    pygame.draw.rect(
        screen,
        VALGE,
        (0, RIBA_KÕRGUS, CANVAS_WIDTH, HEIGHT - RIBA_KÕRGUS)
    )


    for grid_x in range(12, CANVAS_WIDTH, 24):

        pygame.draw.line(
            screen,
            RUUDUSTIK,
            (grid_x, RIBA_KÕRGUS),
            (grid_x, HEIGHT),
            1
        )


    for grid_y in range(RIBA_KÕRGUS + 12, HEIGHT, 24):

        pygame.draw.line(
            screen,
            RUUDUSTIK,
            (0, grid_y),
            (CANVAS_WIDTH, grid_y),
            1
        )


    # =========================================================
    # ÜLEMINE RIBA
    # =========================================================

    pygame.draw.rect(
        screen,
        HALL,
        (
            0,
            0,
            CANVAS_WIDTH,
            RIBA_KÕRGUS
        )
    )


    pygame.draw.line(
        screen,
        (216, 226, 230),
        (0, RIBA_KÕRGUS - 1),
        (CANVAS_WIDTH, RIBA_KÕRGUS - 1),
        1
    )


    # =========================================================
    # DETAILI NUPUD
    # =========================================================

    for tüüp, rect, nimi in nupud:

        hiirel = rect.collidepoint(pygame.mouse.get_pos())

        if valitud_tüüp == tüüp:

            taustavärv = HELE_ROHELINE
            äärevärv = ROHELINE

        else:

            taustavärv = VALGE if not hiirel else (232, 241, 244)
            äärevärv = (194, 208, 214)


        pygame.draw.rect(
            screen,
            taustavärv,
            rect,
            border_radius=8
        )


        pygame.draw.rect(
            screen,
            äärevärv,
            rect,
            1,
            border_radius=8
        )


        tekst = font.render(
            nimi,
            True,
            MUST
        )


        screen.blit(
            tekst,
            (
                rect.centerx -
                tekst.get_width() / 2,

                rect.centery -
                tekst.get_height() / 2
            )
        )


    # =========================================================
    # KUSTUTA
    # =========================================================

    if valitud_detail is not None:

        kustuta_värv = HELE_PUNANE

    else:

        kustuta_värv = VALGE


    pygame.draw.rect(
        screen,
        kustuta_värv,
        kustuta_nupp,
        border_radius=8
    )


    pygame.draw.rect(
        screen,
        PUNANE if valitud_detail is not None else (194, 208, 214),
        kustuta_nupp,
        1,
        border_radius=8
    )


    tekst = font.render(
        "Kustuta",
        True,
        MUST
    )


    screen.blit(
        tekst,
        (
            kustuta_nupp.centerx -
            tekst.get_width() / 2,

            kustuta_nupp.centery -
            tekst.get_height() / 2
        )
    )


    pygame.draw.rect(
        screen,
        VALGE,
        tagasi_nupp,
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        (194, 208, 214),
        tagasi_nupp,
        1,
        border_radius=8
    )

    tekst = font.render("Undo", True, MUST)
    screen.blit(
        tekst,
        (
            tagasi_nupp.centerx - tekst.get_width() / 2,
            tagasi_nupp.centery - tekst.get_height() / 2
        )
    )


    pinge = simulatsiooni_tulemus["pinge"]
    vool = simulatsiooni_tulemus["vool"]
    takistus = simulatsiooni_tulemus["takistus"]
    lambi_võimsus = simulatsiooni_tulemus["lambi_võimsus"]

    pygame.draw.rect(
        screen,
        TUMEPANEEL,
        (CANVAS_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
    )

    pygame.draw.line(
        screen,
        (52, 72, 81),
        (CANVAS_WIDTH, 0),
        (CANVAS_WIDTH, HEIGHT),
        1
    )

    paneeli_x = CANVAS_WIDTH + 24

    tekst = väike_font.render("ELEKTRISKEEM", True, PANEELI_VAIKNE)
    screen.blit(tekst, (paneeli_x, 20))

    tekst = pealkirja_font.render("Mõõteriistad", True, PANEELI_TEKS)
    screen.blit(tekst, (paneeli_x, 39))

    oleku_riba = pygame.Rect(paneeli_x, 86, SIDEBAR_WIDTH - 48, 38)
    if lamp_läbi_põlenud:

        olek = "PIRN LÄBI PÕLENUD"
        oleku_värv = (111, 58, 57)

    elif lamp_põleb:

        olek = "PIRN PÕLEB"
        oleku_värv = (31, 111, 82)

    elif simulatsiooni_tulemus["suletud"]:

        olek = "VOOL LIIGA VÄIKE"
        oleku_värv = (119, 91, 42)

    else:

        olek = "AHEL AVATUD"
        oleku_värv = (111, 58, 57)


    pygame.draw.rect(screen, oleku_värv, oleku_riba, border_radius=7)

    oleku_tekst = font.render(olek, True, VALGE)
    screen.blit(
        oleku_tekst,
        (
            oleku_riba.centerx - oleku_tekst.get_width() / 2,
            oleku_riba.centery - oleku_tekst.get_height() / 2
        )
    )

    takistuse_tekst = (
        f"{takistus:.3g} Ω"
        if math.isfinite(takistus)
        else "∞ Ω"
    )

    mõõdikud = [
        ("LAMBI KLEMMIPINGE", f"{pinge:.3g} V"),
        ("EKVIVALENTTAKISTUS", takistuse_tekst),
        ("VOOL", f"{vool:.3g} A"),
        ("LAMBI VÕIMSUS", f"{lambi_võimsus:.3g} W")
    ]

    for indeks, (silt, väärtus) in enumerate(mõõdikud):

        y = 143 + indeks * 58
        screen.blit(
            väike_font.render(silt, True, PANEELI_VAIKNE),
            (paneeli_x, y)
        )
        screen.blit(
            arvu_font.render(väärtus, True, PANEELI_TEKS),
            (paneeli_x, y + 17)
        )

        if indeks < len(mõõdikud) - 1:

            pygame.draw.line(
                screen,
                (52, 72, 81),
                (paneeli_x, y + 51),
                (WIDTH - 24, y + 51),
                1
            )


    pygame.draw.line(
        screen,
        (52, 72, 81),
        (paneeli_x, 386),
        (WIDTH - 24, 386),
        1
    )

    screen.blit(
        pealkirja_font.render("Detaili väärtus", True, PANEELI_TEKS),
        (paneeli_x, 398)
    )

    if valitud_detail is not None and valitud_detail.tüüp == "takisti":

        välja_silt = "TAKISTUS"
        välja_väärtus = f"{valitud_detail.takistus:g}"
        ühik = "Ω"

    elif valitud_detail is not None and valitud_detail.tüüp == "lamp":

        välja_silt = "LAMBI TAKISTUS"
        välja_väärtus = f"{valitud_detail.takistus:g}"
        ühik = "Ω"

    elif valitud_detail is not None and valitud_detail.tüüp == "vooluallikas":

        välja_silt = "ALLIKA PINGE"
        välja_väärtus = f"{valitud_detail.pinge:g}"
        ühik = "V"

    else:

        välja_silt = "VALI TAKISTI, LAMP VÕI ALLIKAS"
        välja_väärtus = ""
        ühik = ""

    screen.blit(
        väike_font.render(välja_silt, True, PANEELI_VAIKNE),
        (paneeli_x, 435)
    )

    välja_ääre = PUNANE if sisendi_viga else ROHELINE if muudetav_väli else (74, 96, 104)
    välja_taust = (35, 53, 62) if välja_väärtus else (31, 45, 53)
    pygame.draw.rect(screen, välja_taust, omaduse_väli, border_radius=7)
    pygame.draw.rect(screen, välja_ääre, omaduse_väli, 2 if muudetav_väli else 1, border_radius=7)

    kuvatav_väärtus = välja_tekst if muudetav_väli else välja_väärtus
    väärtuse_tekst = font.render(kuvatav_väärtus, True, PANEELI_TEKS)
    screen.blit(
        väärtuse_tekst,
        (omaduse_väli.x + 13, omaduse_väli.centery - väärtuse_tekst.get_height() / 2)
    )

    ühiku_tekst = font.render(ühik, True, PANEELI_VAIKNE)
    screen.blit(
        ühiku_tekst,
        (omaduse_väli.right - ühiku_tekst.get_width() - 13,
         omaduse_väli.centery - ühiku_tekst.get_height() / 2)
    )

    kui_tekst = "Vajuta Enter, et rakendada" if muudetav_väli else "Klõpsa väärtusel muutmiseks"
    screen.blit(
        väike_font.render(kui_tekst, True, PANEELI_VAIKNE),
        (paneeli_x, 520)
    )

    if sisendi_viga:

        screen.blit(
            väike_font.render("Sisesta arv, mis on suurem kui 0", True, (255, 145, 135)),
            (paneeli_x, 542)
        )

    pygame.draw.line(
        screen,
        (52, 72, 81),
        (paneeli_x, HEIGHT - 82),
        (WIDTH - 24, HEIGHT - 82),
        1
    )

    screen.blit(
        väike_font.render("Ctrl+Z  Samm tagasi", True, PANEELI_VAIKNE),
        (paneeli_x, HEIGHT - 62)
    )

    screen.blit(
        väike_font.render("Parema klahviga pööra detaili", True, PANEELI_VAIKNE),
        (paneeli_x, HEIGHT - 38)
    )


    # =========================================================
    # LAUAL OLEVAD DETAILID
    # =========================================================

    screen.set_clip(
        pygame.Rect(
            0,
            RIBA_KÕRGUS,
            CANVAS_WIDTH,
            HEIGHT - RIBA_KÕRGUS
        )
    )

    for detail in detailid:

        detail.joonista(
            screen,
            detail == valitud_detail,
            simulatsiooni_tulemus["lambid_põlevad"].get(detail, False),
            detail.läbi_põlenud
        )


    # =========================================================
    # KÄES OLEV DETAIL
    # =========================================================

    if käes_olev is not None:

        käes_olev.joonista(
            screen,
            True,
            False,
            False
        )


    screen.set_clip(None)


    # =========================================================
    # EKRAANI UUENDAMINE
    # =========================================================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()


