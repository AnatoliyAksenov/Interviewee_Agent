import os
import yaml
import random


levels = ["Junior", "Middle", "Senior"]
fields = ["маркетинг", "разработка", "продажи", "логистика", "HR", "финансы"]
personalities = ["уверенный", "застенчивый", "разговорчивый", "заносчивый", "скромный"]
soft_skills = ["проактивность", "командная работа", "коммуникации", "критическое мышление", "гибкость"]
styles = ["формальный", "неформальный", "полуформальный"]
    
    
def load_profiles(filename: str) -> dict:
    """
    Loads person profiles from YAML file located in the utils directory.
    """
    current_dir = os.path.dirname(os.path.dirname(__file__))
    profiles_file = os.path.join(current_dir, "profiles", filename)
    with open(profiles_file, "r") as file:
        return yaml.safe_load(file)


def generate_candidate():
    level = random.choice(levels)
    field = random.choice(fields)
    personality = random.choice(personalities)
    skills = random.sample(soft_skills, 2)
    style = random.choice(styles)
    
    return {
        "Имя": random.choice(["Алексей", "Марина", "Игорь", "Екатерина", "Дмитрий"]),
        "Уровень": level,
        "Сфера": field,
        "Личность": personality,
        "Ключевые soft skills": skills,
        "Стиль общения": style,
        "Цель": random.choice([
            "найти более интересные проекты",
            "перейти в международную компанию",
            "повысить доход",
            "сменить сферу",
            "избежать выгорания"
        ])
    }

def render_candidate_profile(candidate):
    profile = []
    
    profile.append(f"Имя: {candidate['name']}")
    profile.append(f"Возраст: {candidate['age']}")
    profile.append(f"Позиция: {candidate['position']}")
    profile.append(f"Образование: {candidate['education']}")
    profile.append(f"Опыт: {candidate['experience_years']} лет")
    
    profile.append("\nОпыт работы:")
    for job in candidate["work_history"]:
        profile.append(f"— {job['period']} | {job['position']} в {job['company']}: {job['description']}")
    
    profile.append("\nХард скилы:")
    for skill in candidate["hard_skills"]:
        profile.append(f"• {skill}")
    
    profile.append("\nСофт скилы:")
    for skill in candidate["soft_skills"]:
        profile.append(f"• {skill}")
    
    profile.append("\nЛичностные качества:")
    for trait in candidate["personal_traits"]:
        profile.append(f"• {trait}")
    
    profile.append("\nИстории (по методике STAR):")
    for story in candidate["stories"]:
        profile.append(f"\n - Навык: {story['skill']}\n{story['story']}")
    

    return "\n".join(profile)
