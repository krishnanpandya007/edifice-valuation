# 🏢 Edifice Valuation

**A full-stack web application for real estate valuation processes, built with Django, DRF, and PostgreSQL.**  
This platform is designed to streamline and digitize traditional property valuation workflows for professionals.

## 🚀 Features

- 🔐 Secure login system with role-based access  
- 📑 Form-based dynamic data input system  
- 🧠 Intelligent logic to compute land/building values  
- 🖨️ Ready-to-export report formats  
- ☁️ Cloud-hosted & scalable backend (Render)  
- 🛠️ Modular design for future expansion

## 🧱 Tech Stack

| Layer        | Technologies Used                           |
|--------------|---------------------------------------------|
| Frontend     | HTML, CSS (via Django Templates)            |
| Backend      | Python, Django, Django REST Framework (DRF) |
| Database     | PostgreSQL                                  |
| Deployment   | Render.com                                  |
| Dev Tools    | Git, VS Code, Postman                       |

## ⚙️ Getting Started (Local Setup)


```bash
git clone https://github.com/krishnanpandya007/edifice-valuation.git
cd edifice-valuation

python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
## 📌 Future Enhancements

- Generate downloadable PDF valuation reports  
- Add visualization charts for summary analytics  
- Implement frontend with React/Flutter  
- Add support for multiple regional formats

## 👨‍💻 Author

**Krishnan Pandya**  
[LinkedIn](https://www.linkedin.com/in/krishnanpandya) | [GitHub](https://github.com/krishnanpandya007)  
Freelance Full-Stack Developer | Cloud & AI Enthusiast

---

## 📜 License

This project is licensed under the MIT License.
