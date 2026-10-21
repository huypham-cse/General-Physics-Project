# Vehicle Ejection Simulation

Mô phỏng ghế phóng theo 7 phương trình trong file Word: chuyển động trên ray, bay có lực cản, vượt đuôi máy bay và điều kiện bung dù. Các file JSON mẫu dùng bộ số minh họa.

## Chạy nhanh

Mở PowerShell tại thư mục dự án:

```powershell
cd "D:\General Physics\VehicleEjectionSimulation"
python -m pip install -r requirements.txt
python main.py
```

Lệnh mặc định đọc `inputs/example.json` và ghi kết quả vào `outputs/example/`.

Chạy một input khác:

```powershell
python main.py --input inputs/tail_collision.json
python main.py --input inputs/no_deployment.json
```

Tự chọn nơi lưu hoặc chỉ xuất dữ liệu:

```powershell
python main.py --input inputs/example.json --output outputs/my_run
python main.py --input inputs/example.json --no-plots
```

## Thay đổi input

Sao chép `inputs/example.json`, sửa giá trị rồi truyền đường dẫn qua `--input`. JSON dùng dấu chấm cho số thập phân và không chứa comment.

| Nhóm | Biến | Ý nghĩa và đơn vị |
| --- | --- | --- |
| `launch` | `average_gun_force` | Lực phóng trung bình, N |
| `launch` | `rail_angle_deg` | Góc ray so với chiều bay, độ; lớn hơn 90° là nghiêng về sau |
| `launch` | `rail_length` | Chiều dài ray, m |
| `launch` | `tail_offset` | Khoảng cách đuôi nằm sau điểm rời ray, m |
| `launch` | `tail_top_height` | Đỉnh đuôi cao hơn điểm rời ray bao nhiêu, m |
| `launch` | `clearance_margin` | Khoảng cách an toàn phía trên đỉnh đuôi, m |
| `seat` | `total_mass` | Tổng khối lượng ghế và phi công, kg |
| `seat` | `drag_coefficient` | Hệ số cản của ghế |
| `seat` | `frontal_area_A` | Diện tích cản gió của ghế, m² |
| `aircraft` | `speed` | Vận tốc máy bay, m/s |
| `aircraft` | `initial_altitude` | Độ cao điểm rời ray so với mặt đất, m |
| `constants` | `gravity` | Gia tốc trọng trường, m/s² |
| `constants` | `air_density` | Khối lượng riêng không khí, kg/m³ |
| `simulation` | `max_time` | Thời gian tối đa sau khi rời ray, s |
| `simulation` | `time_step` | Bước thời gian Euler, s |
| `parachute` | `drag_coefficient` | Hệ số cản của dù |
| `parachute` | `area` | Diện tích cản gió của dù, m² |
| `parachute` | `max_deceleration` | Giới hạn giảm tốc khi mở dù, m/s²; Word dùng 150 |
| `parachute` | `deployment_altitude` | Độ cao tối đa cho phép bung dù, m; Word dùng 3000 |

Mọi hằng số vật lý và ngưỡng đều được đọc từ input. Thử giảm `time_step` để kiểm tra độ ổn định của kết quả. Nếu lực phóng không đủ tạo gia tốc dương trên ray, chương trình báo lỗi.

## Đọc kết quả

Mỗi lần chạy tạo một thư mục gồm:

- `input.json`: bản sao thông số đã chạy.
- `summary.txt`: kết quả dễ đọc.
- `summary.json`: kết quả dạng JSON.
- `trajectory.csv`: thời gian, vị trí, vận tốc, gia tốc, vị trí đuôi và giảm tốc dự kiến khi mở dù. Có thể mở bằng Excel.
- `trajectory.png`: quỹ đạo ghế và các thời điểm kiểm tra.
- `motion.png`: vận tốc và gia tốc theo thời gian.
- `tail_clearance.png`: khoảng cách ngang với đuôi và độ cao vượt đuôi.
- `parachute_conditions.png`: hai điều kiện bung dù.

Chạy lại cùng thư mục sẽ ghi đè các file cùng tên. Dùng `--output` khác nếu muốn giữ kết quả cũ. `--no-plots` bỏ qua bước tạo ảnh; ảnh từ lần chạy trước trong cùng thư mục vẫn còn.

`model_status` trong `summary.json` có ba giá trị:

- `met`: vượt đuôi đủ khoảng cách và có thời điểm bung dù hợp lệ.
- `not_met`: không vượt đuôi đủ khoảng cách, hoặc chạm đất trước khi đủ điều kiện bung dù.
- `incomplete`: chưa kiểm tra được đủ hai điều kiện trong đoạn mô phỏng. Có thể cần tăng `max_time`.

Kết quả đánh giá các điều kiện của mô hình trong Word. Mô phỏng kết thúc khi bung dù, chạm đất hoặc hết thời gian; chưa tính chuyển động hạ cánh dưới dù. PT (6) và thời điểm bung dù được kiểm tra theo từng bước `time_step`. Nếu chạm đất, mẫu cuối có thể có độ cao âm nhỏ do Euler; đó là mẫu vượt qua mặt đất, không phải vị trí đáp chính xác.

## Các file chính

| File | Chức năng |
| --- | --- |
| `main.py` | Đọc và kiểm tra JSON, chạy mô phỏng, xuất CSV và báo cáo |
| `physics_model.py` | Các công thức theo thứ tự (1)–(7) và điều phối mô hình |
| `solvers.py` | Một bước cập nhật bằng phương pháp Euler |
| `visualizations/plots.py` | Tạo và lưu bốn biểu đồ |
| `inputs/` | Các kịch bản đầu vào |
| `outputs/` | Kết quả mỗi lần chạy |
