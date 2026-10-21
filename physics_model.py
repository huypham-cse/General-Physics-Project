import math


# PT (1): a = F_gun / m - g * sin(theta), u = sqrt(2 * a * L)
# Tinh gia toc tren ray va toc do cua ghe so voi may bay.
def angle(theta_deg):  # theta_deg: goc ray tinh bang do, dung cho PT (1), (2).
    return math.radians(theta_deg)  # Doi sang radian de dung sin va cos.


def acceleration(
    F_gun,  # Luc ban trung binh (N), PT (1).
    m,      # Tong khoi luong ghe va phi cong (kg), PT (1).
    g,      # Gia toc trong truong (m/s^2), PT (1).
    theta,  # Goc ray so voi phuong ngang (radian), PT (1).
):
    a = F_gun / m - g * math.sin(theta)  # Gia toc doc theo ray (m/s^2), PT (1).
    if a <= 0:
        raise ValueError("Gia toc tren ray phai lon hon 0")
    return a


def velocity(
    a,  # Gia toc tren ray (m/s^2), PT (1).
    L,  # Chieu dai ray (m), PT (1).
):
    u = math.sqrt(2 * a * L)  # Toc do roi ray so voi may bay (m/s), PT (1).
    return u


# PT (2): v0 = v_A * x_hat + u * u_hat
# Chieu theo x va y: v0x = v_A + u * cos(theta), v0y = u * sin(theta).
def initial_velocity(
    v_A,    # Van toc may bay theo phuong x (m/s), PT (2).
    u,      # Toc do ghe so voi may bay (m/s), tu PT (1).
    theta,  # Goc ray so voi phuong ngang (radian), PT (2).
):
    # Neu theta > 90 do thi ray nghieng ve phia sau may bay.
    vx0 = v_A + u * math.cos(theta)  # Van toc ghe theo x luc roi ray (m/s), PT (2).
    vy0 = u * math.sin(theta)        # Van toc ghe theo y luc roi ray (m/s), PT (2).
    return vx0, vy0


# PT (3): m * dv/dt = m * g_vector + F_D
# Chon y huong len: ax = F_D_x / m, ay = -g + F_D_y / m.
def free_flight_acceleration(
    F_D_x,  # Luc can theo x (N), lay tu PT (4).
    F_D_y,  # Luc can theo y (N), lay tu PT (4).
    m,      # Tong khoi luong ghe va phi cong (kg), PT (3).
    g,      # Do lon gia toc trong truong (m/s^2), PT (3).
):
    ax = F_D_x / m       # Gia toc theo x (m/s^2), PT (3).
    ay = -g + F_D_y / m  # Gia toc theo y (m/s^2), PT (3).
    return ax, ay


# PT (4): F_D = -(1/2) * rho * C_D * A * |v| * v_vector
# Luc can nguoc chieu van toc. Khong khi dung yen nhu gia thiet trong Word.
def drag_force(
    vx,   # Van toc hien tai theo x (m/s), PT (4).
    vy,   # Van toc hien tai theo y (m/s), PT (4).
    rho,  # Khoi luong rieng khong khi (kg/m^3), PT (4).
    C_D,  # He so can cua ghe, khong co don vi, PT (4).
    A,    # Dien tich can gio cua ghe (m^2), PT (4).
):
    v = math.sqrt(vx**2 + vy**2)      # Do lon van toc |v| (m/s), PT (4).
    k = rho * C_D * A / 2            # Phan he so chung cua luc can, PT (4).
    F_D_x = -k * v * vx              # Thanh phan luc can theo x (N), PT (4).
    F_D_y = -k * v * vy              # Thanh phan luc can theo y (N), PT (4).
    return F_D_x, F_D_y


# PT (5): x_tail(t) = -d + v_A * t, y_tail = y0 + h
# Word chon x0 = 0. Neu nhap x0 khac 0 thi cong them x0 vao x_tail.
def tail_position(
    d,     # Khoang cach duoi nam sau diem roi ray (m), PT (5).
    h,     # Do cao dinh duoi so voi diem roi ray (m), PT (5).
    v_A,   # Van toc may bay (m/s), PT (5).
    y0,    # Do cao diem roi ray so voi mat dat (m), PT (5).
    t,     # Thoi gian tinh tu luc roi ray (s), PT (5).
    x0=0.0,  # Vi tri x cua diem roi ray (m); bang 0 trong Word.
):
    x_tail = x0 - d + v_A * t  # Vi tri ngang cua duoi tai t (m), PT (5).
    y_tail = y0 + h           # Do cao dinh duoi (m), PT (5).
    return x_tail, y_tail


# PT (6): y_seat(t_c) >= y0 + h + delta
# t_c la lan dau x_seat = x_tail. margin trong code chinh la delta trong Word.
# Code lay buoc dau tien x_tail >= x_seat de tinh gan dung t_c theo dt.
def tail_clearance(
    results,  # Danh sach trang thai ghe tinh tu PT (3), (4).
    d,        # Khoang cach duoi nam sau diem roi ray (m), PT (5).
    h,        # Do cao dinh duoi so voi diem roi ray (m), PT (5), (6).
    margin,   # Khoang cach an toan delta (m), PT (6).
    v_A,      # Van toc may bay (m/s), PT (5).
    y0,       # Do cao diem roi ray (m), PT (5), (6).
    x0=0.0,   # Vi tri x cua diem roi ray (m), mac dinh nhu Word.
):
    for state in results:  # state: trang thai ghe tai mot buoc thoi gian.
        t_c = state["time_t"]  # Thoi diem dang kiem tra (s), dung tim t_c cua PT (6).
        x_seat = state["pos_x"]  # Vi tri ngang cua ghe (m), dung tim luc duoi bat kip.
        x_tail, y_tail = tail_position(d, h, v_A, y0, t_c, x0)  # Vi tri duoi (m), PT (5).

        # Lay buoc dau tien duoi bat kip hoac vuot vi tri ngang cua ghe.
        if x_tail >= x_seat:
            y_seat = state["pos_y"]  # Do cao ghe tai buoc bat kip (m), PT (6).
            cleared = y_seat >= y_tail + margin  # True neu ghe vuot duoi du khoang an toan, PT (6).

            return {
                "time_t": t_c,        # Thoi diem bat kip gan dung theo dt (s).
                "tail_x": x_tail,     # Vi tri x cua duoi tai buoc kiem tra (m).
                "seat_y": y_seat,     # Do cao ghe tai buoc kiem tra (m).
                "tail_y": y_tail,     # Do cao dinh duoi (m).
                "cleared": cleared,  # Ket qua dieu kien PT (6).
            }

    # None: chua tim thay luc gap trong doan da mo phong, chua ket luan an toan.
    return None


# PT (7): rho * C_D_p * A_p * v^2 / (2 * m) <= a_max
# Dung he so can va dien tich cua DU, khac voi ghe trong PT (4).
# Dieu kien y <= deploy_altitude duoc viet bang loi trong Word, khong co so PT.
def parachute_deployment(
    results,         # Cac trang thai ghe truoc khi bung du, tu PT (3), (4).
    m,               # Tong khoi luong ghe va phi cong (kg), PT (7).
    rho,             # Khoi luong rieng khong khi (kg/m^3), PT (7).
    C_D_p,           # He so can cua du, khong co don vi, PT (7).
    A_p,             # Dien tich can gio cua du (m^2), PT (7).
    a_max,           # Gioi han giam toc khi bung du (m/s^2), PT (7).
    deploy_altitude,  # Do cao toi da de bung du (m), dieu kien B trong Word.
):
    for state in results:  # state: vi tri, van toc va gia toc tai mot thoi diem.
        if state["time_t"] > 0 and state["pos_y"] <= 0:
            break  # Ghe da cham dat thi dung kiem tra.
        if state["vel_y"] > 0:
            continue  # Ghe con di len thi chua kiem tra bung du.

        v = math.sqrt(state["vel_x"]**2 + state["vel_y"]**2)  # Toc do tai luc xet bung du (m/s).
        a_drag = rho * C_D_p * A_p * v**2 / (2 * m)  # Do lon giam toc do luc can cua du (m/s^2), PT (7).
        safe_speed = a_drag <= a_max                    # Dieu kien A: thoa PT (7).
        safe_altitude = state["pos_y"] <= deploy_altitude  # Dieu kien B: du thap de bung du.

        # Lay mau dau tien thoa ca hai dieu kien khi ghe dang roi.
        if safe_speed and safe_altitude:
            return {
                "time_t": state["time_t"],  # Thoi diem bung du (s), gan dung theo buoc dt.
                "pos_x": state["pos_x"],    # Vi tri ngang khi bung du (m).
                "pos_y": state["pos_y"],    # Do cao khi bung du (m).
                "speed": v,                # Toc do khi bung du (m/s).
                "drag_acceleration": a_drag,  # Giam toc du kien khi bung du (m/s^2), PT (7).
            }

    return None  # Chua du dieu kien bung du trong thoi gian mo phong.


# Phan tinh so: dung PT (3), (4) de cap nhat chuyen dong bang Euler.
# Euler la cach tinh gan dung trong Python, khong nam trong 7 PT cua Word.
def simulate(
    vx0,      # Van toc ban dau theo x (m/s), tu PT (2).
    vy0,      # Van toc ban dau theo y (m/s), tu PT (2).
    m,        # Tong khoi luong (kg), PT (3).
    rho,      # Khoi luong rieng khong khi (kg/m^3), PT (4).
    C_D,      # He so can cua ghe, PT (4).
    A,        # Dien tich can gio cua ghe (m^2), PT (4).
    g,        # Gia toc trong truong (m/s^2), PT (3).
    dt,       # Buoc thoi gian (s), dung cho Euler.
    duration,  # Thoi gian mo phong toi da sau khi roi ray (s).
    y0=0.0,   # Do cao diem roi ray (m), dieu kien dau trong Word.
    x0=0.0,   # Vi tri ngang diem roi ray (m), Word chon bang 0.
):
    x = x0    # Vi tri x_seat (m), dung tim luc gap trong PT (6).
    y = y0    # Do cao y_seat (m), dung trong PT (6) va dieu kien B.
    vx = vx0  # Van toc ghe theo x (m/s), gia tri dau tu PT (2), dung trong PT (4).
    vy = vy0  # Van toc ghe theo y (m/s), gia tri dau tu PT (2), dung trong PT (4).
    time = 0.0  # Thoi gian tu luc roi ray (s); day la moc t = 0 trong Word.
    results = []  # Luu trang thai ghe sau moi buoc tinh.

    while time <= duration:
        F_D_x, F_D_y = drag_force(vx, vy, rho, C_D, A)  # Hai thanh phan luc can (N), PT (4).
        ax, ay = free_flight_acceleration(F_D_x, F_D_y, m, g)  # Hai thanh phan gia toc (m/s^2), PT (3).

        results.append({
            "time_t": time,  # Thoi gian (s).
            "pos_x": x,      # Vi tri theo x (m).
            "pos_y": y,      # Do cao (m).
            "vel_x": vx,     # Van toc theo x (m/s).
            "vel_y": vy,     # Van toc theo y (m/s).
            "ax": ax,        # Gia toc theo x (m/s^2), PT (3), (4).
            "ay": ay,        # Gia toc theo y (m/s^2), PT (3), (4).
        })

        if y <= 0 and time > 0:
            break  # Dung khi ghe cham dat; do cao co the lech mot buoc Euler.

        step = min(dt, duration - time)  # Buoc tinh hien tai (s), khong vuot duration.
        if step <= 0:
            break

        # Dung vi tri va van toc cu de tinh buoc moi theo Euler.
        x = x + vx * dt
        y = y + vy * dt
        vx = vx + ax * dt
        vy = vy + ay * dt
        time += step     # Sang thoi diem tiep theo (s).

    return results


# Ham chinh: doc input, goi cac cong thuc va gom ket qua.
def simulate_ejection(
    config,             # Cac nhom input duoi day, don vi SI.
    initial_state=None,  # Neu co: (x0, y0, vx0, vy0) tai luc roi ray; None thi tu tinh.
):
    launch = config["launch"]          # Input ve sung ban, ray va vi tri duoi.
    seat = config["seat"]              # Input ve khoi luong va luc can cua ghe.
    aircraft = config["aircraft"]      # Input ve van toc va do cao may bay.
    constants = config["constants"]    # Input ve g va khoi luong rieng khong khi.
    simulation = config["simulation"]  # Input ve thoi gian va buoc tinh.
    parachute = config["parachute"]    # Input ve du va dieu kien bung du.

    # Doc bien theo thu tu xuat hien trong 7 PT.
    F_gun = launch["average_gun_force"]  # Luc ban trung binh (N), PT (1).
    m = seat["total_mass"]              # Khoi luong ghe + phi cong (kg), PT (1), (3), (7).
    g = constants["gravity"]            # Gia toc trong truong (m/s^2), PT (1), (3).
    theta_deg = launch["rail_angle_deg"]  # Goc ray so voi phuong ngang (do), PT (1), (2).
    theta = angle(theta_deg)            # Goc ray doi sang radian cho sin va cos.
    L = launch["rail_length"]           # Chieu dai ray (m), PT (1).
    v_A = aircraft["speed"]             # Van toc may bay (m/s), PT (2), (5).
    y0 = aircraft["initial_altitude"]   # Do cao luc roi ray (m), dieu kien dau va PT (5), (6).
    rho = constants["air_density"]      # Khoi luong rieng khong khi (kg/m^3), PT (4), (7).
    C_D = seat["drag_coefficient"]      # He so can cua ghe, PT (4).
    A = seat["frontal_area_A"]          # Dien tich can gio cua ghe (m^2), PT (4).
    d = launch["tail_offset"]           # Khoang cach duoi nam sau diem roi ray (m), PT (5).
    h = launch["tail_top_height"]       # Do cao dinh duoi so voi diem roi ray (m), PT (5), (6).
    margin = launch["clearance_margin"]  # Khoang cach an toan delta (m), PT (6).
    C_D_p = parachute["drag_coefficient"]  # He so can cua du, PT (7).
    A_p = parachute["area"]             # Dien tich can gio cua du (m^2), PT (7).
    a_max = parachute["max_deceleration"]  # Gioi han giam toc (m/s^2), PT (7); Word dung 150.
    deploy_altitude = parachute["deployment_altitude"]  # Nguong do cao (m), dieu kien B; Word dung 3000.
    duration = simulation["max_time"]   # Thoi gian mo phong toi da (s), khong phai hang so vat ly.
    dt = simulation["time_step"]        # Buoc tinh Euler (s); nho hon thuong cho ket qua sat hon.

    # Kiem tra input truoc khi tinh.
    if m <= 0 or L <= 0 or g <= 0 or dt <= 0 or duration <= 0:
        raise ValueError("Khoi luong, chieu dai ray, g va thoi gian phai lon hon 0")
    if F_gun < 0 or rho < 0 or C_D < 0 or A < 0:
        raise ValueError("Luc ban va cac gia tri luc can khong duoc am")
    if C_D_p < 0 or A_p < 0 or a_max < 0 or deploy_altitude < 0:
        raise ValueError("Cac gia tri cua du khong duoc am")
    if d <= 0 or h < 0 or margin < 0 or y0 < 0:
        raise ValueError("Vi tri duoi may bay va do cao khong hop le")

    a = acceleration(F_gun, m, g, theta)       # Gia toc tren ray (m/s^2), PT (1).
    u = velocity(a, L)                        # Toc do ghe so voi may bay (m/s), PT (1).
    vx0, vy0 = initial_velocity(v_A, u, theta)  # Van toc ghe so voi dat luc roi ray (m/s), PT (2).
    x0 = 0.0                                 # Chon goc x tai diem roi ray nhu Word.
    if initial_state is not None:
        x0, y0, vx0, vy0 = initial_state  # Dung dieu kien dau tu input neu duoc truyen vao.

    results = simulate(
        vx0, vy0, m, rho, C_D, A, g, dt, duration, y0, x0
    )  # Quy dao ghe tinh bang Euler tu PT (3), (4).

    clearance = tail_clearance(
        results, d, h, margin, v_A, y0, x0
    )  # Ket qua vuot duoi, PT (5), (6).

    deployment = parachute_deployment(
        results, m, rho, C_D_p, A_p, a_max, deploy_altitude
    )  # Thoi diem dau thoa PT (7) va dieu kien do cao khi ghe dang roi.

    # Chi giu quy dao den luc bung du, vi sau do luc can se thay doi.
    if deployment is not None:
        for i in range(len(results)):  # i: vi tri cua mau trong danh sach ket qua.
            if results[i]["time_t"] == deployment["time_t"]:
                results = results[:i + 1]  # Giu tu mau dau den ca mau bung du.
                break
        # Neu duoi chi bat kip sau luc bung du thi chua ket luan trong mo hinh nay.
        if clearance is not None and clearance["time_t"] > deployment["time_t"]:
            clearance = None

    return {
        "launch_acceleration": a,          # Gia toc tren ray (m/s^2), PT (1).
        "ejection_speed": u,               # Toc do ghe so voi may bay (m/s), PT (1).
        "release_velocity": (vx0, vy0),    # Hai thanh phan van toc roi ray (m/s), PT (2).
        "trajectory": results,            # Cac mau chuyen dong tu PT (3), (4).
        "tail_clearance": clearance,      # Ket qua PT (5), (6); None neu chua tim thay luc gap.
        "parachute_deployment": deployment,  # Ket qua PT (7) va dieu kien B; None neu chua bung du.
    }
