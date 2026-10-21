def euler_step(x, y, vx, vy, ax, ay, dt):
    x_new = x + vx * dt
    y_new = y + vy * dt
    vx_new = vx + ax * dt
    vy_new = vy + ay * dt
    return x_new, y_new, vx_new, vy_new
