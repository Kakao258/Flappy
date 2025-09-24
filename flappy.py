import pygame, sys, random, os, json

pygame.init()
largeur, hauteur = 400, 600
fenetre = pygame.display.set_mode((largeur, hauteur))
clock = pygame.time.Clock()
pygame.display.set_caption("Flappy Bird")

# Dossiers
IMG_DIR = "Skin"
BG_DIR = "Fond"
SOUND_DIR = "sounds"
MUSIC_DIR = "music"

# Couleurs
BLEU_CIEL = (135, 206, 250)
VERT = (0, 200, 0)
ORANGE = (255, 165, 0)
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
GRIS = (230, 230, 230)
GRIS_FONCE = (60, 60, 60)
ROUGE = (220, 50, 50)

# Polices
font = pygame.font.SysFont("Arial", 32)
font_big = pygame.font.SysFont("Arial", 48, bold=True)
font_small = pygame.font.SysFont("Arial", 22)
font_admin = pygame.font.SysFont("Arial", 18)

# Physique
gravite = 0.5
saut = -8
vitesse_base = 3
vitesse_scroll = vitesse_base

# États
STATE_MENU = "MENU"
STATE_PLAY = "PLAYING"
STATE_OVER = "GAME_OVER"
STATE_SKINS = "SKINS"
STATE_ADMIN = "ADMIN"
STATE_PARAMS = "PARAMS"
state = STATE_MENU

# Volume musique et SFX
musique_volume = 1.0
sfx_volume = 1.0

# Mode auto
auto_mode = False
jeu_auto = False

# Boutons
btn_w, btn_h = 200, 50
btn_play_rect = pygame.Rect(largeur // 2 - btn_w // 2, 240, btn_w, btn_h)
btn_skin_rect = pygame.Rect(largeur // 2 - btn_w // 2, 310, btn_w, btn_h)
btn_param_rect = pygame.Rect(largeur // 2 - btn_w // 2, 380, btn_w, btn_h)
btn_quit_rect = pygame.Rect(largeur // 2 - btn_w // 2, 450, btn_w, btn_h)
btn_admin_rect = pygame.Rect(largeur - 110, 10, 100, 40)
btn_auto_rect = pygame.Rect(10, 10, 180, 40)  # Bouton Mode Auto un peu plus large

# Skins
skins = {
    "Jaune": {"bird": os.path.join(IMG_DIR, "flappo.png"), "bg": os.path.join(BG_DIR, "fond.png"), "prix": 0, "taille": 45},
    "Rouge": {"bird": os.path.join(IMG_DIR, "ruby.png"), "bg": os.path.join(BG_DIR, "fond.png"), "prix": 10, "taille": 45},
    "Bleu": {"bird": os.path.join(IMG_DIR, "skibidi.png"), "bg": os.path.join(BG_DIR, "fond.png"), "prix": 15, "taille": 45},
    "Violet": {"bird": os.path.join(IMG_DIR, "skouizi.png"), "bg": os.path.join(BG_DIR, "fond.png"), "prix": 20, "taille": 45}
}

# Sauvegarde
save_file = "save_data.json"
if os.path.exists(save_file):
    with open(save_file, "r") as f:
        data = json.load(f)
    highscore = data.get("highscore", 0)
    pieces = data.get("pieces", 0)
    skin_couleur = data.get("skin_couleur", "Jaune")
    skins_achetes = set(data.get("skins_achetes", ["Jaune"]))
    musique_volume = data.get("musique_volume", 1.0)
    sfx_volume = data.get("sfx_volume", 1.0)
    auto_mode = data.get("auto_mode", False)
else:
    highscore = 0
    pieces = 0
    skin_couleur = "Jaune"
    skins_achetes = {"Jaune"}
    musique_volume = 1.0
    sfx_volume = 1.0
    auto_mode = False

# Sons
skin_sounds = {}
for name in skins.keys():
    skin_sounds[name] = {
        "score": pygame.mixer.Sound(os.path.join(SOUND_DIR, "point.wav")) if os.path.exists(os.path.join(SOUND_DIR, "point.wav")) else None,
        "flap": pygame.mixer.Sound(os.path.join(SOUND_DIR, "wing.wav")) if os.path.exists(os.path.join(SOUND_DIR, "wing.wav")) else None,
        "hit": pygame.mixer.Sound(os.path.join(SOUND_DIR, "thud sound effect.wav")) if os.path.exists(os.path.join(SOUND_DIR, "thud sound effect.wav")) else None,
    }

def apply_volume():
    try:
        pygame.mixer.music.set_volume(musique_volume)
    except Exception:
        pass
    for sdict in skin_sounds.values():
        for snd in sdict.values():
            if snd is not None:
                try:
                    snd.set_volume(sfx_volume)
                except Exception:
                    pass

# Musique personnalisée skin
def play_skin_music(skin_name):
    pygame.mixer.music.stop()
    if skin_name == "Rouge":
        music_file = os.path.join(MUSIC_DIR, "angry_bird.wav")
        if os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(musique_volume)
            except Exception:
                pass
    else:
        pygame.mixer.music.stop()

play_skin_music(skin_couleur)
apply_volume()

# ----------------------------------------------------
# Images
skin_images = {}
skin_buttons = []
for i, (name, assets) in enumerate(skins.items()):
    taille = assets["taille"]
    try:
        bird_img = pygame.image.load(assets["bird"]).convert_alpha()
        bird_img = pygame.transform.scale(bird_img, (taille, taille))
    except:
        bird_img = pygame.Surface((taille, taille), pygame.SRCALPHA)
        bird_img.fill((255, 255, 0))
    try:
        bg_img = pygame.image.load(assets["bg"]).convert()
        bg_img = pygame.transform.scale(bg_img, (largeur, hauteur))
    except:
        bg_img = pygame.Surface((largeur, hauteur))
        bg_img.fill(BLEU_CIEL)
    skin_images[name] = {"bird": bird_img, "bg": bg_img}

    x = 80 + i * (taille + 20)
    rect = pygame.Rect(x, 250, taille, taille)
    skin_buttons.append((rect, name))

# ----------------------------------------------------
# Variables jeu
oiseau_x = 100
oiseau_y = hauteur // 2
vitesse = 0
tuyaux = []
pieces_en_jeu = []
score = 0
vitesse_scroll = vitesse_base
tuyaux_passes = 0
PIECE_SIZE = 20
ESPACEMENT_BASE = 300
ESPACEMENT_VITESSE = 50

# Variables apprentissage IA
ia_offset = 0.0  # Ajustement dynamique de l'IA pour apprendre

# Fonctions de jeu
def save_game():
    with open(save_file, "w") as f:
        json.dump({
            "highscore": highscore,
            "pieces": pieces,
            "skin_couleur": skin_couleur,
            "skins_achetes": list(skins_achetes),
            "musique_volume": musique_volume,
            "sfx_volume": sfx_volume,
            "auto_mode": auto_mode
        }, f)

def creer_tuyau(premier=False):
    hauteur_tuyau = random.randint(180, 380) if not premier else random.randint(220, 400)
    espace = 160
    bas = pygame.Rect(largeur, hauteur_tuyau, 60, hauteur)
    haut = pygame.Rect(largeur, 0, 60, hauteur_tuyau - espace)
    return [bas, haut]

def creer_piece():
    x = largeur + random.randint(200, 600)
    y = random.randint(100, hauteur - 100)
    return pygame.Rect(x, y, PIECE_SIZE, PIECE_SIZE)

def reset_game():
    global oiseau_x, oiseau_y, vitesse, tuyaux, score, vitesse_scroll, pieces_en_jeu, tuyaux_passes, ia_offset
    oiseau_x = 100
    oiseau_y = hauteur // 2
    vitesse = saut
    tuyaux = []
    pieces_en_jeu = []
    tuyaux.extend(creer_tuyau(premier=True))
    tuyaux.extend(creer_tuyau())
    if len(tuyaux) >= 4:
        tuyaux[2].x += 300
        tuyaux[3].x += 300
    score = 0
    vitesse_scroll = vitesse_base
    tuyaux_passes = 0
    ia_offset = 0.0

def draw_text_center(surface, texte, police, couleur, y):
    img = police.render(texte, True, couleur)
    x = (largeur - img.get_width()) // 2
    surface.blit(img, (x, y))

def draw_button(rect, texte, hovered=False, font_used=None, couleur_fond=None):
    if font_used is None: font_used = font
    if couleur_fond is None: couleur_fond = GRIS if not hovered else GRIS_FONCE
    pygame.draw.rect(fenetre, couleur_fond, rect, border_radius=10)
    pygame.draw.rect(fenetre, NOIR, rect, width=2, border_radius=10)
    txt = font_used.render(texte, True, BLANC if hovered else NOIR)
    fenetre.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

# -----------------------
# Boucle principale
reset_game()
while True:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_game()
            pygame.quit(); sys.exit()

        if state == STATE_MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reset_game(); jeu_auto = False; state = STATE_PLAY
                elif event.key == pygame.K_s: state = STATE_SKINS
                elif event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_play_rect.collidepoint(event.pos):
                    reset_game(); jeu_auto = False; state = STATE_PLAY
                elif btn_skin_rect.collidepoint(event.pos): state = STATE_SKINS
                elif btn_param_rect.collidepoint(event.pos): state = STATE_PARAMS
                elif btn_quit_rect.collidepoint(event.pos): pygame.quit(); sys.exit()
                elif btn_admin_rect.collidepoint(event.pos): state = STATE_ADMIN
                elif btn_auto_rect.collidepoint(event.pos):
                    auto_mode = not auto_mode
                    save_game()

        elif state == STATE_PLAY:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = STATE_MENU
            # Les touches normales ne fonctionnent pas si auto_mode = True
            if not auto_mode:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    vitesse = saut
                    if skin_sounds.get(skin_couleur, {}).get("flap"):
                        skin_sounds[skin_couleur]["flap"].play()

        elif state == STATE_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: reset_game(); state = STATE_PLAY; jeu_auto = False
                elif event.key == pygame.K_BACKSPACE: state = STATE_MENU
                elif event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        elif state == STATE_SKINS:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, name in skin_buttons:
                    if rect.collidepoint(event.pos):
                        if name in skins_achetes:
                            skin_couleur = name
                            play_skin_music(name)
                            save_game()
                            state = STATE_MENU
                        elif pieces >= skins[name]["prix"]:
                            pieces -= skins[name]["prix"]
                            skin_couleur = name
                            skins_achetes.add(name)
                            play_skin_music(name)
                            save_game()
                            state = STATE_MENU
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = STATE_MENU

        elif state == STATE_ADMIN:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(50,500,120,40).collidepoint(event.pos):
                    pieces += 10; save_game()
                if pygame.Rect(200,500,120,40).collidepoint(event.pos):
                    pieces = 0; save_game()
                if btn_admin_rect.collidepoint(event.pos):
                    highscore = 0; save_game()
                if pygame.Rect(125,550,150,40).collidepoint(event.pos):
                    skins_achetes = {"Jaune"}; save_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = STATE_MENU

        elif state == STATE_PARAMS:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = STATE_MENU
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Rectangles pour boutons volumes
                vol_plus_mus_rect = pygame.Rect(largeur//2 + 80, 250, 40, 40)
                vol_moins_mus_rect = pygame.Rect(largeur//2 - 120, 250, 40, 40)
                vol_plus_sfx_rect = pygame.Rect(largeur//2 + 80, 300, 40, 40)
                vol_moins_sfx_rect = pygame.Rect(largeur//2 - 120, 300, 40, 40)

                # Musique
                if vol_plus_mus_rect.collidepoint(event.pos) and musique_volume < 1.0:
                    musique_volume = min(1.0, round(musique_volume + 0.05, 2))
                    apply_volume()
                    save_game()
                elif vol_moins_mus_rect.collidepoint(event.pos) and musique_volume > 0.0:
                    musique_volume = max(0.0, round(musique_volume - 0.05, 2))
                    apply_volume()
                    save_game()
                # SFX
                elif vol_plus_sfx_rect.collidepoint(event.pos) and sfx_volume < 1.0:
                    sfx_volume = min(1.0, round(sfx_volume + 0.05, 2))
                    apply_volume()
                    save_game()
                elif vol_moins_sfx_rect.collidepoint(event.pos) and sfx_volume > 0.0:
                    sfx_volume = max(0.0, round(sfx_volume - 0.05, 2))
                    apply_volume()
                    save_game()

    # -----------------------
    # LOGIQUE
    if state == STATE_PLAY:
        vitesse += gravite
        oiseau_y += vitesse
        for t in tuyaux: t.x -= vitesse_scroll
        for p in pieces_en_jeu: p.x -= vitesse_scroll

        # Mode auto intelligent avec anticipation et apprentissage
        if auto_mode:
            prochain_tuyau = None
            for t in tuyaux:
                if t.x + t.width > oiseau_x:
                    prochain_tuyau = t
                    break

            if prochain_tuyau:
                if prochain_tuyau.top < hauteur / 2:  # tuyau haut
                    espace_haut = prochain_tuyau.bottom
                    espace_bas = prochain_tuyau.bottom + 160
                else:  # tuyau bas
                    espace_haut = prochain_tuyau.top - 160
                    espace_bas = prochain_tuyau.top

                centre_espace = (espace_haut + espace_bas) / 2 + ia_offset

                # Anticipation : ajuster si le tuyau est loin
                distance = prochain_tuyau.x - oiseau_x
                facteur_anticipe = max(1, distance / 100)
                cible_y = centre_espace - vitesse * facteur_anticipe

                if oiseau_y + skins[skin_couleur]["taille"]/2 > cible_y:
                    vitesse = saut
                    if skin_sounds.get(skin_couleur, {}).get("flap"):
                        skin_sounds[skin_couleur]["flap"].play()

            # Ajustement dynamique IA (apprentissage simple)
            if tuyaux_passes > 0 and score > 0 and score % 3 == 0:
                ia_offset *= 0.95  # réduit petit à petit l’erreur
            if oiseau_y < 0:
                vitesse = 2
            elif oiseau_y + skins[skin_couleur]["taille"] > hauteur:
                vitesse = saut

        # Ajouter tuyaux
        espacement = ESPACEMENT_BASE + int(vitesse_scroll*ESPACEMENT_VITESSE/10)
        if len(tuyaux) >= 2 and tuyaux[-2].x < largeur - espacement:
            tuyaux.extend(creer_tuyau())

        # Ajouter pièces aléatoires
        if random.random() < 0.01:
            pieces_en_jeu.append(creer_piece())

        # Suppression tuyaux passés
        if len(tuyaux) >= 2 and tuyaux[0].x < -60:
            tuyaux = tuyaux[2:]
            score += 1
            tuyaux_passes += 1
            ia_offset += random.uniform(-5,5)  # apprentissage par ajustement aléatoire
            if tuyaux_passes % 3 == 0:
                vitesse_scroll += 0.1

        # Collision oiseau-tuyaux
        taille_skin = skins[skin_couleur]["taille"]
        hitbox_w, hitbox_h = int(taille_skin*0.7), int(taille_skin*0.7)
        oiseau_rect = pygame.Rect(oiseau_x + (taille_skin-hitbox_w)//2, int(oiseau_y)+(taille_skin-hitbox_h)//2, hitbox_w, hitbox_h)

        if oiseau_y > hauteur or any(oiseau_rect.colliderect(t) for t in tuyaux):
            state = STATE_OVER
            if skin_sounds.get(skin_couleur, {}).get("hit"):
                skin_sounds[skin_couleur]["hit"].play()
            if score > highscore:
                highscore = score
                save_game()

        # Collision pièces
        for p in pieces_en_jeu[:]:
            if oiseau_rect.colliderect(p):
                pieces += 1
                pieces_en_jeu.remove(p)
                if skin_sounds.get(skin_couleur, {}).get("score"):
                    skin_sounds[skin_couleur]["score"].play()
                save_game()

    # -----------------------
    # Rendu
    fenetre.blit(skin_images[skin_couleur]["bg"], (0,0))

    # MENU
    if state == STATE_MENU:
        draw_text_center(fenetre, "Flappy Bird", font_big, NOIR, 120)
        draw_button(btn_play_rect, "Jouer", btn_play_rect.collidepoint(mouse_pos))
        draw_button(btn_skin_rect, "Skins", btn_skin_rect.collidepoint(mouse_pos))
        draw_button(btn_param_rect, "Paramètres", btn_param_rect.collidepoint(mouse_pos))
        draw_button(btn_quit_rect, "Quitter", btn_quit_rect.collidepoint(mouse_pos))
        draw_button(btn_admin_rect, "ADMIN", btn_admin_rect.collidepoint(mouse_pos), font_admin)

        couleur_auto = VERT if auto_mode else ROUGE
        draw_button(btn_auto_rect, f"Mode Auto: {'ON' if auto_mode else 'OFF'}", btn_auto_rect.collidepoint(mouse_pos), font_small, couleur_auto)

        fenetre.blit(skin_images[skin_couleur]["bird"], (oiseau_x, hauteur//2))
        draw_text_center(fenetre, f"Highscore: {highscore}", font_small, NOIR, 50)
        draw_text_center(fenetre, f"Pieces: {pieces}", font_small, ORANGE, 80)

    # PLAY
    elif state == STATE_PLAY:
        fenetre.blit(skin_images[skin_couleur]["bird"], (oiseau_x, int(oiseau_y)))
        for t in tuyaux: pygame.draw.rect(fenetre, VERT, t)
        for p in pieces_en_jeu: pygame.draw.circle(fenetre, ORANGE, p.center, PIECE_SIZE//2)
        draw_text_center(fenetre, str(score), font, NOIR, 20)
        draw_text_center(fenetre, f"Highscore: {highscore}", font_small, NOIR, 50)
        draw_text_center(fenetre, f"Pieces: {pieces}", font_small, ORANGE, 80)
        if auto_mode:
            draw_text_center(fenetre, "MODE AUTO ACTIVÉ", font_small, ROUGE, 10)

    # GAME OVER
    elif state == STATE_OVER:
        fenetre.blit(skin_images[skin_couleur]["bird"], (oiseau_x, int(oiseau_y)))
        for t in tuyaux: pygame.draw.rect(fenetre, VERT, t)
        draw_text_center(fenetre, "GAME OVER", font_big, ROUGE, 200)
        draw_text_center(fenetre, f"Score : {score}", font, BLANC, 260)
        draw_text_center(fenetre, f"Highscore : {highscore}", font_small, BLANC, 290)
        draw_text_center(fenetre, "ESPACE = Rejouer", font_small, BLANC, 330)
        draw_text_center(fenetre, "RETOUR = Menu", font_small, BLANC, 360)

    # SKINS
    elif state == STATE_SKINS:
        draw_text_center(fenetre, "Choisissez un skin", font, NOIR, 150)
        draw_text_center(fenetre, f"Pieces: {pieces}", font_small, ORANGE, 200)
        for rect, name in skin_buttons:
            fenetre.blit(skin_images[name]["bird"], (rect.x, rect.y))
            pygame.draw.rect(fenetre, NOIR, rect, 2)
            if name not in skins_achetes:
                couleur_prix = ORANGE if pieces >= skins[name]['prix'] else ROUGE
                txt = font_small.render(f"{skins[name]['prix']} pcs", True, couleur_prix)
                fenetre.blit(txt, (rect.x, rect.y + skins[name]["taille"] + 5))

    # ADMIN
    elif state == STATE_ADMIN:
        draw_text_center(fenetre, "MODE ADMIN", font_big, ROUGE, 100)
        draw_button(pygame.Rect(50,500,120,40), "Ajouter 10 pcs", False, font_admin)
        draw_button(pygame.Rect(200,500,120,40), "Reset pcs", False, font_admin)
        draw_button(btn_admin_rect, "Reset HS", False, font_admin)
        draw_button(pygame.Rect(125,550,150,40), "Reset Skins", False, font_admin)
        draw_text_center(fenetre, f"Highscore: {highscore}", font_small, NOIR, 200)
        draw_text_center(fenetre, f"Pieces: {pieces}", font_small, ORANGE, 240)

    # PARAMS
    elif state == STATE_PARAMS:
        draw_text_center(fenetre, "Paramètres", font_big, NOIR, 120)

        # Musique
        vol_plus_mus_rect = pygame.Rect(largeur//2 + 80, 250, 40, 40)
        vol_moins_mus_rect = pygame.Rect(largeur//2 - 120, 250, 40, 40)
        draw_button(vol_plus_mus_rect, "+", vol_plus_mus_rect.collidepoint(mouse_pos))
        draw_button(vol_moins_mus_rect, "-", vol_moins_mus_rect.collidepoint(mouse_pos))
        txt_musique = font_small.render("Musique", True, NOIR)
        txt_musique_val = font_small.render(f"{int(musique_volume*100)}%", True, NOIR)
        fenetre.blit(txt_musique, (vol_moins_mus_rect.x - txt_musique.get_width() - 10, vol_moins_mus_rect.y + 5))
        fenetre.blit(txt_musique_val, (vol_plus_mus_rect.x + vol_plus_mus_rect.width + 10, vol_plus_mus_rect.y + 5))

        # SFX
        vol_plus_sfx_rect = pygame.Rect(largeur//2 + 80, 300, 40, 40)
        vol_moins_sfx_rect = pygame.Rect(largeur//2 - 120, 300, 40, 40)
        draw_button(vol_plus_sfx_rect, "+", vol_plus_sfx_rect.collidepoint(mouse_pos))
        draw_button(vol_moins_sfx_rect, "-", vol_moins_sfx_rect.collidepoint(mouse_pos))
        txt_sfx = font_small.render("SFX", True, NOIR)
        txt_sfx_val = font_small.render(f"{int(sfx_volume*100)}%", True, NOIR)
        fenetre.blit(txt_sfx, (vol_moins_sfx_rect.x - txt_sfx.get_width() - 10, vol_moins_sfx_rect.y + 5))
        fenetre.blit(txt_sfx_val, (vol_plus_sfx_rect.x + vol_plus_sfx_rect.width + 10, vol_plus_sfx_rect.y + 5))

        apply_volume()
        draw_text_center(fenetre, "ESC = Retour", font_small, NOIR, 350)

    pygame.display.flip()
    clock.tick(60)
