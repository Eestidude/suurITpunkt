import pygame
import math
import copy

pygame.init()

# =========================================================
# AKEN
# =========================================================

WIDTH = 1000
HEIGHT = 650

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elektriskeemi koostaja")

clock = pygame.time.Clock()


# =========================================================
# VÄRVID
# =========================================================

VALGE = (255, 255, 255)
MUST = (0, 0, 0)

HALL = (190, 190, 190)
HELE_HALL = (230, 230, 230)

ROHELINE = (40, 190, 70)
HELE_ROHELINE = (190, 255, 200)

PUNANE = (230, 70, 70)
HELE_PUNANE = (255, 190, 190)

KOLLANE = (255, 220, 0)
HELE_KOLLANE = (255, 245, 80)

SININE = (60, 150, 255)


# =========================================================
# FONDID
# =========================================================

font = pygame.font.SysFont(None, 23)
väike_font = pygame.font.SysFont(None, 18)


# =========================================================
# SEADISTUSED
# =========================================================

RIBA_KÕRGUS = 60

DETAILI_LAIUS = 60
DETAILI_KÕRGUS = 40

JUHTME_PIKKUS = 90

ÜHENDUSE_KAUGUS = 25
KONTAKTI_KAUGUS = 14


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
        lamp_põleb=False
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


        # =================================================
        # LAMP
        # =================================================

        elif self.tüüp == "lamp":

            if lamp_põleb:

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
# KAS KAKS DETAILI ON ÜHENDATUD
# =========================================================

def on_ühendatud(
    detail1,
    detail2
):

    for a in detail1.kontaktid():

        for b in detail2.kontaktid():

            if kaugus(
                a,
                b
            ) <= 4:

                return True


    return False


# =========================================================
# GRAAF
# =========================================================

def ehita_graaf():

    graaf = {}

    for detail in detailid:

        graaf[detail] = []


    for i in range(
        len(detailid)
    ):

        for j in range(
            i + 1,
            len(detailid)
        ):

            a = detailid[i]
            b = detailid[j]


            if on_ühendatud(
                a,
                b
            ):

                graaf[a].append(b)
                graaf[b].append(a)


    return graaf


# =========================================================
# AHELA KONTROLL
# =========================================================

def kas_ahel_on_korras():

    allikas = None
    lamp = None
    takisti = None


    for detail in detailid:

        if detail.tüüp == "vooluallikas":

            allikas = detail

        elif detail.tüüp == "lamp":

            lamp = detail

        elif detail.tüüp == "takisti":

            takisti = detail


    if allikas is None:
        return False

    if lamp is None:
        return False

    if takisti is None:
        return False


    # Vajame vähemalt ühte juhet.

    on_juhe = False

    for detail in detailid:

        if detail.tüüp == "juhe":

            on_juhe = True
            break


    if not on_juhe:
        return False


    graaf = ehita_graaf()


    # -----------------------------------------------------
    # Otsime kõik allikast ühendatud detailid.
    # -----------------------------------------------------

    nähtud = set()

    järjekord = [allikas]


    while järjekord:

        praegune = järjekord.pop()


        if praegune in nähtud:
            continue


        nähtud.add(
            praegune
        )


        for järgmine in graaf[praegune]:

            if järgmine not in nähtud:

                järjekord.append(
                    järgmine
                )


    if lamp not in nähtud:
        return False

    if takisti not in nähtud:
        return False


    # -----------------------------------------------------
    # Kontrollime, et allika mõlemad otsad on kasutuses.
    # -----------------------------------------------------

    allika_kontaktid = (
        allikas.kontaktid()
    )


    esimese_kontakti_detailid = []

    teise_kontakti_detailid = []


    for detail in detailid:

        if detail is allikas:
            continue


        for kontakt in detail.kontaktid():

            if kaugus(
                allika_kontaktid[0],
                kontakt
            ) <= 4:

                esimese_kontakti_detailid.append(
                    detail
                )


            if kaugus(
                allika_kontaktid[1],
                kontakt
            ) <= 4:

                teise_kontakti_detailid.append(
                    detail
                )


    if not esimese_kontakti_detailid:
        return False

    if not teise_kontakti_detailid:
        return False


    # -----------------------------------------------------
    # Kontrollime teed ühelt allika otsalt teisele.
    # -----------------------------------------------------

    for algus in esimese_kontakti_detailid:

        järjekord = [
            (
                algus,
                algus is lamp,
                algus is takisti
            )
        ]

        külastatud = set()


        while järjekord:

            praegune, lamp_leitud, takisti_leitud = (
                järjekord.pop()
            )


            lamp_nüüd = (
                lamp_leitud
                or
                praegune is lamp
            )


            takisti_nüüd = (
                takisti_leitud
                or
                praegune is takisti
            )


            võti = (
                praegune,
                lamp_nüüd,
                takisti_nüüd
            )


            if võti in külastatud:
                continue


            külastatud.add(
                võti
            )


            if praegune in teise_kontakti_detailid:

                if (
                    lamp_nüüd
                    and
                    takisti_nüüd
                ):

                    return True


            for järgmine in graaf[praegune]:

                järjekord.append(
                    (
                        järgmine,
                        lamp_nüüd,
                        takisti_nüüd
                    )
                )


    return False


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
            10,
            10,
            110,
            40
        ),
        "Takisti"
    ),

    (
        "lamp",
        pygame.Rect(
            125,
            10,
            100,
            40
        ),
        "Lamp"
    ),

    (
        "vooluallikas",
        pygame.Rect(
            230,
            10,
            140,
            40
        ),
        "Vooluallikas"
    ),

    (
        "juhe",
        pygame.Rect(
            375,
            10,
            90,
            40
        ),
        "Juhe"
    )
]


kustuta_nupp = pygame.Rect(
    475,
    10,
    100,
    40
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


# =========================================================
# PEAMINE TSÜKKEL
# =========================================================

töötab = True


while töötab:

    # =====================================================
    # SÜNDMUSED
    # =====================================================

    for event in pygame.event.get():

        # =================================================
        # SULGEMINE
        # =================================================

        if event.type == pygame.QUIT:

            töötab = False


        # =================================================
        # KLAVIATUUR
        # =================================================

        elif event.type == pygame.KEYDOWN:

            if (
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


                # =================================================
                # TÖÖALA
                # =================================================

                if not nuppudele_vajutus:

                    # =============================================
                    # DETAIL ON KÄES
                    # =============================================

                    if käes_olev is not None:

                        if my > RIBA_KÕRGUS:

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
    # LAMBI KONTROLL
    # =========================================================

    lamp_põleb = kas_ahel_on_korras()


    # =========================================================
    # TAUST
    # =========================================================

    screen.fill(
        VALGE
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
            WIDTH,
            RIBA_KÕRGUS
        )
    )


    # =========================================================
    # DETAILI NUPUD
    # =========================================================

    for tüüp, rect, nimi in nupud:

        if valitud_tüüp == tüüp:

            värv = HELE_ROHELINE

        else:

            värv = VALGE


        pygame.draw.rect(
            screen,
            värv,
            rect
        )


        pygame.draw.rect(
            screen,
            MUST,
            rect,
            2
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
        kustuta_nupp
    )


    pygame.draw.rect(
        screen,
        MUST,
        kustuta_nupp,
        2
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


    # =========================================================
    # AHELA OLEK
    # =========================================================

    if lamp_põleb:

        olek = "AHEL ON SULETUD"
        oleku_värv = (20, 140, 40)

    else:

        olek = "AHEL ON AVATUD"
        oleku_värv = (190, 40, 40)


    tekst = font.render(
        olek,
        True,
        oleku_värv
    )


    screen.blit(
        tekst,
        (
            600,
            8
        )
    )


    # =========================================================
    # JUHISED
    # =========================================================

    if käes_olev is not None:

        juhend = (
            "Detail on käes | "
            "Vasak hiir: aseta | "
            "Parem hiir: pööra 90°"
        )

    elif valitud_detail is not None:

        juhend = (
            "Lohista detaili | "
            "Juhtme otsa lohistades venitad juhet | "
            "Parem hiir: pööra"
        )

    else:

        juhend = (
            "Vali detail | "
            "Ctrl+Z: samm tagasi | "
            "Kustuta: eemalda valitud detail"
        )


    tekst = väike_font.render(
        juhend,
        True,
        MUST
    )


    screen.blit(
        tekst,
        (
            600,
            37
        )
    )


    # =========================================================
    # LAUAL OLEVAD DETAILID
    # =========================================================

    for detail in detailid:

        detail.joonista(
            screen,
            detail == valitud_detail,
            lamp_põleb
        )


    # =========================================================
    # KÄES OLEV DETAIL
    # =========================================================

    if käes_olev is not None:

        käes_olev.joonista(
            screen,
            True,
            False
        )


    # =========================================================
    # EKRAANI UUENDAMINE
    # =========================================================

    pygame.display.flip()

    clock.tick(60)


pygame.quit()


