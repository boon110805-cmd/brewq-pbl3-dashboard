BREWQ – PBL3 QCMS Dashboard (Blue Edition)
Giao diện dùng tông xanh dương lấy cảm hứng từ màu sắc hiện đại của sản phẩm bia và hệ thống giám sát công nghiệp.
DỮ LIỆU TRONG CSV LÀ DỮ LIỆU MÔ PHỎNG, KHÔNG PHẢI SỐ LIỆU THỰC TẾ CỦA 7 BRIDGES.

Chạy trong Terminal PyCharm:
python -m pip install -r requirements.txt
python -m streamlit run app.py

Menu: Tổng quan, Dữ liệu, X-chart, R-chart, C-chart (OOS), P-chart (OOS), Năng lực, Run Test, Phân tích.
Bộ CSV demo gồm 60 mẻ, 5 phép đo thể tích chiết rót/mẻ để minh họa X-bar/R, số lỗi và số đơn vị kiểm tra để minh họa C/P chart.
Các giới hạn kỹ thuật trong app.py chỉ là minh họa. Không dùng kết quả mô phỏng để tuyên bố chất lượng/năng lực quá trình thực tế.
