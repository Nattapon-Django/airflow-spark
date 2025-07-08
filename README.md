# 🚀 Airflow & Spark ETL Pipeline

โปรเจกต์นี้คือระบบ ETL (Extract, Transform, Load) ที่ใช้ **Apache Airflow** สำหรับการจัดการ Workflow และ **Apache Spark** สำหรับการประมวลผลข้อมูลขนาดใหญ่ โดยทั้งหมดทำงานอยู่บนสภาพแวดล้อมแบบ Dockerized ถูกออกแบบมาเพื่อย้ายและแปลงข้อมูลจาก Oracle ไปยัง PostgreSQL อย่างมีประสิทธิภาพ

---

## ✨ คุณสมบัติเด่น (Features)

*   **Dockerized Environment**: ติดตั้งง่ายและมีสภาพแวดล้อมที่สอดคล้องกันด้วย Docker และ Docker Compose
*   **ETL Pipelines**: ชุดของ DAGs สำหรับการย้ายข้อมูลจาก Oracle ไปยัง PostgreSQL
*   **Apache Spark Integration**: ใช้ประโยชน์จาก Spark Cluster (1 Master, 3 Workers) เพื่อการประมวลผลข้อมูลขนาดใหญ่และมีประสิทธิภาพสูง
*   **Jupyter Notebook Integration**: มาพร้อมกับ Jupyter Notebook ที่เชื่อมต่อกับ PySpark สำหรับการทดลองและพัฒนาโค้ดแบบ Interactive
*   **Monitoring & Alerting**: ระบบแจ้งเตือนผ่าน Microsoft Teams เมื่อ Pipeline ทำงานผิดพลาด
*   **Data Lineage**: สามารถเชื่อมต่อกับ DataHub เพื่อติดตามการไหลของข้อมูล (Data Lineage)
*   **Dynamic DAGs**: ตัวอย่างการสร้าง DAGs แบบไดนามิกเพื่อจัดการกับหลายๆ ตารางพร้อมกัน

---

## 🏗️ สถาปัตยกรรม (Architecture)

โปรเจกต์นี้ใช้ Docker Compose ในการจัดการคอนเทนเนอร์ต่างๆ ดังนี้:

*   **Apache Airflow**: เป็นหัวใจหลักในการควบคุมการทำงาน (Orchestrator) ประกอบด้วย Webserver, Scheduler, และ Worker ที่ทำงานในคอนเทนเนอร์ของตัวเอง
*   **Apache Spark**: เป็นเอนจิ้นในการประมวลผล (Processing Engine) ประกอบด้วย Spark Master และ Workers สำหรับรันงานที่ถูกส่งมาจาก Airflow
*   **JupyterLab**: สภาพแวดล้อมสำหรับการพัฒนาเชิงโต้ตอบ (Interactive Development Environment) ที่มาพร้อม PySpark สำหรับการทดลองและสร้างต้นแบบของ Spark jobs
*   **PostgreSQL**: ทำหน้าที่เป็นฐานข้อมูลเบื้องหลัง (Backend Database) ให้กับ Airflow

---

## 🚀 การติดตั้งและใช้งาน (Getting Started)

### สิ่งที่ต้องมี (Prerequisites)

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)

### ขั้นตอนการติดตั้ง (Installation & Setup)

1.  **Clone โปรเจกต์นี้**
    ```bash
    # git clone <your-repo-url>
    # cd <your-repo-name>
    ```

2.  **สร้างโฟลเดอร์ที่จำเป็นและไฟล์ .env**
    คำสั่งนี้จะช่วยให้ไฟล์ที่สร้างโดยคอนเทนเนอร์มีสิทธิ์ (Ownership) ที่ถูกต้อง
    ```bash
    mkdir -p ./dags ./logs ./plugins ./config ./notebooks
    echo -e "AIRFLOW_UID=$(id -u)" > .env
    ```

3.  **Pull Docker images ที่จำเป็น**
    ```bash
    docker compose pull
    ```

4.  **Build custom images ของโปรเจกต์**
    ```bash
    docker compose build
    ```

5.  **เริ่มต้นฐานข้อมูลของ Airflow** (ทำเพียงครั้งเดียว)
    ```bash
    docker compose up airflow-init
    ```

6.  **รัน Service ทั้งหมดใน Background**
    ```bash
    docker compose up -d
    ```

---

## 🌐 การเข้าถึง Services (Service Endpoints)

หลังจากรัน Service ทั้งหมดแล้ว คุณสามารถเข้าถึงหน้าเว็บต่างๆ ได้ที่:

*   **Airflow UI**: `http://localhost:8080`
    *   **Username**: `admin`
    *   **Password**: `admin`

*   **Spark Master UI**: `http://localhost:8181`
    *   ดูสถานะของ Spark cluster, workers, และ application ที่กำลังรันอยู่

*   **Jupyter Notebook UI**: `http://localhost:8888`
    *   **Token**: `admin`
    *   พื้นที่สำหรับทดลองและพัฒนาโค้ด PySpark

---

## 📂 โครงสร้างโปรเจกต์ (Project Structure)

```
.
├── dags/            # โฟลเดอร์สำหรับเก็บไฟล์ DAGs ของ Airflow
├── notebooks/       # โฟลเดอร์สำหรับ Jupyter Notebooks (.ipynb)
├── spark/           # โค้ดสำหรับ Spark Application
│   ├── app/         # โค้ด .py ที่จะถูกส่งไปรันบน Spark
│   └── resources/   # ไฟล์อื่นๆ เช่น jars, data files
├── logs/            # โฟลเดอร์สำหรับเก็บ Log จากการรัน DAGs
├── plugins/         # โฟลเดอร์สำหรับ Custom Airflow Plugins
├── config/          # ไฟล์ตั้งค่าต่างๆ
├── docker-compose.yaml # ไฟล์นิยาม Services ของ Docker
└── Dockerfile       # Dockerfile สำหรับสร้าง Custom Airflow Image
```