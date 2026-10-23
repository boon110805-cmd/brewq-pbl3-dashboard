import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="BREWQ | PBL3 QCMS",page_icon="🍺",layout="wide")
st.markdown("""<style>
:root { --brew-blue:#123B66; --sky-blue:#2D78B7; --ice:#EAF4FC; --foam:#F7FBFF; }
.block-container{padding-top:1.4rem;max-width:1450px}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#123B66 0%,#18578B 100%)}
[data-testid="stSidebar"] *{color:#F7FBFF}
div[data-testid="stMetric"]{background:#EFF7FD;border:1px solid #CFE3F4;padding:13px;border-radius:13px}
h1,h2,h3{color:#123B66}
.stTabs [data-baseweb="tab-list"]{gap:8px}
.stTabs [data-baseweb="tab"]{background:#EAF4FC;border-radius:8px 8px 0 0}
</style>""",unsafe_allow_html=True)
LIMITS={
"mashing_pH":{"label":"Mashing pH","unit":"pH","lsl":5.20,"usl":5.40,"target":5.30},
"original_gravity_P":{"label":"Original Gravity","unit":"°P","lsl":11.70,"usl":12.50,"target":12.10},
"fermentation_temperature_C":{"label":"Fermentation temperature","unit":"°C","lsl":18.00,"usl":21.00,"target":19.50},
"packaging_CO2_vol":{"label":"Packaging CO₂","unit":"vol","lsl":2.20,"usl":2.80,"target":2.50},
"fill_volume_mL":{"label":"Fill volume","unit":"mL","lsl":326.00,"usl":334.00,"target":330.00}}
st.sidebar.markdown("# BREWQ")
st.sidebar.caption("QUALITY MONITOR · PBL3")
page=st.sidebar.radio("ĐIỀU HƯỚNG",["Tổng quan","Dữ liệu","X-chart","R-chart","C-chart (OOS)","P-chart (OOS)","Năng lực","Run Test","Phân tích"])
uploaded=st.sidebar.file_uploader("Tải CSV",type=["csv"])
default=Path(__file__).with_name("simulated_beach_blonde_ale_data.csv")
if uploaded: data=pd.read_csv(uploaded); source="CSV tải lên – cần xác minh nguồn"
elif default.exists(): data=pd.read_csv(default); source="CSV mô phỏng đi kèm"
else: st.error("Không tìm thấy CSV cạnh app.py."); st.stop()
required=["measurement_date","batch_id",*LIMITS]
missing=[c for c in required if c not in data.columns]
if missing: st.error("CSV thiếu cột: "+", ".join(missing)); st.stop()
data["measurement_date"]=pd.to_datetime(data["measurement_date"],errors="coerce")
data=data.dropna(subset=["measurement_date"]).sort_values("measurement_date")
for c in LIMITS: data[c]=pd.to_numeric(data[c],errors="coerce")
st.title("BREWQ | Quality Control")
st.caption("PBL3 · Beach Blonde Ale 330 mL · 7 Bridges Brewing Company")
st.warning("CHẾ ĐỘ MÔ PHỎNG — Dữ liệu SIM-BB và giới hạn minh họa không phải dữ liệu thật hoặc tiêu chuẩn đã được doanh nghiệp xác nhận.")

def chart(x,y,title,ytitle,lines):
    f=go.Figure()
    f.add_trace(go.Scatter(x=x,y=y,mode="lines+markers",name="Giá trị",line={"color":"#2476B8","width":2}))
    for val,label,color,dash in lines: f.add_hline(y=val,annotation_text=label,line_color=color,line_dash=dash)
    f.update_layout(title=title,xaxis_title="Mẻ / thứ tự mẫu",yaxis_title=ytitle,template="plotly_white",height=430,margin=dict(l=15,r=15,t=60,b=15))
    st.plotly_chart(f,use_container_width=True)

def render_ctq(metric):
    cfg=LIMITS[metric]; sub=data.dropna(subset=[metric]); x=sub[metric].astype(float)
    cl=float(x.mean()); sd=float(x.std(ddof=1)); ucl=cl+3*sd; lcl=cl-3*sd
    chart(sub["batch_id"],x,cfg["label"],cfg["unit"],[(ucl,"UCL","#2D78B7","dash"),(cl,"CL","#123B66","solid"),(lcl,"LCL","#2D78B7","dash"),(cfg["usl"],"USL demo","#D28B2D","dot"),(cfg["lsl"],"LSL demo","#D28B2D","dot")])
    st.caption("UCL/CL/LCL: giới hạn kiểm soát minh họa. USL/LSL: giới hạn kỹ thuật minh họa; hai loại giới hạn không đồng nghĩa.")

if page=="Tổng quan":
    st.subheader("01 / Tổng quan chất lượng")
    x=data["fill_volume_mL"].dropna()
    a,b,c,d=st.columns(4); a.metric("Bản ghi",len(data)); b.metric("Nguồn","Mô phỏng" if "SIMULATED" in set(data.get("record_type",[])) else "Cần xác minh")
    c.metric("Ngoài giới hạn kỹ thuật demo",int(((x<326)|(x>334)).sum()))
    c2=float(x.mean()); sd=float(x.std(ddof=1)); d.metric("Trung bình fill",f"{c2:.2f} mL")
    metric=st.selectbox("Chọn CTQ",list(LIMITS),format_func=lambda k:LIMITS[k]["label"]); render_ctq(metric)
    st.info("Prototype học tập; không dùng để kết luận chất lượng thực tế.")
elif page=="Dữ liệu":
    st.subheader("02 / Data explorer"); st.dataframe(data,use_container_width=True,hide_index=True)
    st.download_button("Xuất CSV",data.to_csv(index=False).encode("utf-8-sig"),"brewq_data_export.csv","text/csv")
elif page in ["X-chart","R-chart"]:
    st.subheader("03 / Biểu đồ nhóm mẫu")
    cols=[f"fill_sample_{i}_mL" for i in range(1,6)]
    if not all(c in data for c in cols): st.warning("Cần 5 phép đo lặp cho mỗi nhóm mẫu để dựng X-bar/R.")
    else:
        mat=data[cols].astype(float).to_numpy(); means=mat.mean(axis=1); ranges=mat.max(axis=1)-mat.min(axis=1)
        if page=="X-chart":
            center=means.mean(); rbar=ranges.mean(); ucl=center+.577*rbar; lcl=center-.577*rbar
            chart(data["batch_id"],means,"X-bar chart · Fill volume","Trung bình mL",[(ucl,"UCL","#2D78B7","dash"),(center,"CL","#123B66","solid"),(lcl,"LCL","#2D78B7","dash")])
            st.caption("Dùng A₂ = 0,577 cho nhóm n=5; minh họa bằng dữ liệu mô phỏng.")
        else:
            center=ranges.mean(); ucl=2.114*center; lcl=0
            chart(data["batch_id"],ranges,"R chart · Fill volume","Khoảng biến thiên mL",[(ucl,"UCL","#2D78B7","dash"),(center,"CL","#123B66","solid"),(lcl,"LCL","#2D78B7","dash")])
            st.caption("Dùng D₃ = 0, D₄ = 2,114 cho nhóm n=5; minh họa bằng dữ liệu mô phỏng.")
elif page=="C-chart (OOS)":
    st.subheader("04 / C-chart · Số lỗi")
    col="defect_count_per_inspection_unit"
    if col not in data: st.warning("CSV cần số lỗi và đơn vị kiểm tra cố định.")
    else:
        x=data[col].astype(float); cl=x.mean(); ucl=cl+3*np.sqrt(cl); lcl=max(0,cl-3*np.sqrt(cl))
        chart(data["batch_id"],x,"C-chart · Simulated defect counts","Số lỗi",[(ucl,"UCL","#2D78B7","dash"),(cl,"CL","#123B66","solid"),(lcl,"LCL","#2D78B7","dash")])
        st.caption("C-chart chỉ phù hợp khi cơ hội kiểm tra/đơn vị kiểm tra giữ cố định.")
elif page=="P-chart (OOS)":
    st.subheader("05 / P-chart · Tỷ lệ đơn vị lỗi")
    if not {"defective_units","units_inspected"}.issubset(data): st.warning("CSV cần defective_units và units_inspected.")
    else:
        p=data["defective_units"]/data["units_inspected"]; pbar=data["defective_units"].sum()/data["units_inspected"].sum()
        sig=np.sqrt(pbar*(1-pbar)/data["units_inspected"])
        f=go.Figure(); f.add_trace(go.Scatter(x=data["batch_id"],y=p,mode="lines+markers",name="Tỷ lệ lỗi",line={"color":"#176B57"}))
        f.add_trace(go.Scatter(x=data["batch_id"],y=np.minimum(1,pbar+3*sig),name="UCL",line={"dash":"dash","color":"#2D78B7"}))
        f.add_trace(go.Scatter(x=data["batch_id"],y=np.maximum(0,pbar-3*sig),name="LCL",line={"dash":"dash","color":"#2D78B7"}))
        f.add_hline(y=pbar,annotation_text="CL / p-bar",line_color="#123B66")
        f.update_layout(title="P-chart · Simulated defective proportion",template="plotly_white",height=430)
        st.plotly_chart(f,use_container_width=True)
        st.caption("Giới hạn thay đổi theo cỡ mẫu từng mẻ. Dữ liệu mô phỏng.")
elif page=="Năng lực":
    st.subheader("06 / Năng lực quá trình"); metric=st.selectbox("Chọn CTQ",list(LIMITS),format_func=lambda k:LIMITS[k]["label"])
    cfg=LIMITS[metric]; x=data[metric].dropna().astype(float); mean=x.mean(); sd=x.std(ddof=1)
    cp=(cfg["usl"]-cfg["lsl"])/(6*sd); cpk=min((cfg["usl"]-mean)/(3*sd),(mean-cfg["lsl"])/(3*sd))
    a,b,c=st.columns(3); a.metric("Trung bình",f"{mean:.3f} {cfg['unit']}"); b.metric("Cp demo",f"{cp:.3f}"); c.metric("Cpk demo",f"{cpk:.3f}")
    st.warning("Chỉ số tính trên dữ liệu mô phỏng, không phải bằng chứng năng lực thực tế. Cần kiểm tra ổn định và xác nhận giới hạn kỹ thuật trước khi diễn giải.")
elif page=="Run Test":
    st.subheader("07 / Run Test"); metric=st.selectbox("Chọn CTQ",list(LIMITS),format_func=lambda k:LIMITS[k]["label"])
    x=data[metric].dropna().astype(float).reset_index(drop=True); cl=x.mean(); hits=[]
    side=np.where(x>cl,1,np.where(x<cl,-1,0))
    for i in range(8,len(x)):
        if np.all(side[i-8:i+1]==1) or np.all(side[i-8:i+1]==-1): hits.append((i+1,"9 điểm cùng phía CL",x.iloc[i]))
    for i in range(5,len(x)):
        diff=np.diff(x.iloc[i-5:i+1])
        if np.all(diff>0) or np.all(diff<0): hits.append((i+1,"6 điểm tăng/giảm liên tiếp",x.iloc[i]))
    result=pd.DataFrame(hits,columns=["Vị trí kết thúc","Quy tắc","Giá trị cuối"]).drop_duplicates()
    st.write("Quy tắc demo: 9 điểm cùng phía CL; 6 điểm tăng/giảm liên tiếp.")
    if result.empty: st.success("Không phát hiện chuỗi theo hai quy tắc demo này.")
    else: st.dataframe(result,use_container_width=True,hide_index=True)
    st.caption("Cần đối chiếu quy tắc cuối cùng với yêu cầu của giảng viên.")
elif page=="Phân tích":
    st.subheader("08 / Phân tích chất lượng"); metric=st.selectbox("Chọn CTQ",list(LIMITS),format_func=lambda k:LIMITS[k]["label"])
    cfg=LIMITS[metric]; x=data[metric].dropna().astype(float); cl=x.mean(); sd=x.std(ddof=1)
    outc=int(((x<cl-3*sd)|(x>cl+3*sd)).sum()); outs=int(((x<cfg["lsl"])|(x>cfg["usl"])).sum())
    a,b,c=st.columns(3); a.metric("Trung bình",f"{x.mean():.3f} {cfg['unit']}"); b.metric("Ngoài giới hạn kiểm soát",outc); c.metric("Ngoài giới hạn kỹ thuật demo",outs)
    st.warning("Chỉ mô tả dữ liệu mô phỏng; không suy rộng thành kết luận về sản xuất thật.")
st.markdown("---")
st.caption("BREWQ · PBL3 QCMS prototype · Blue beer-inspired interface · Simulated data only.")
