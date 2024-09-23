from decimal import Decimal

import psycopg2


class DBManager:
    """Класс для работы с БД."""

    def __init__(self, params):
        self.conn = psycopg2.connect(dbname="hh_db", **params)
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self):
        """
        Функция для получения списка всех компаний
        и количество вакансий у каждой компании.
        """

        self.cur.execute(
            """
                    SELECT employer_name, COUNT(vacancies.employer_id)
                    FROM employers
                    INNER JOIN vacancies USING (employer_id)
                    GROUP BY employer_name
                    ORDER BY COUNT DESC
            """
        )

        return self.cur.fetchall()

    def get_all_vacancies(self):
        """Функция для списка всех вакансий с указанием названия компании,
        названия вакансии и зарплаты с ссылкой на вакансию."""

        self.cur.execute(
            """
                    SELECT e.employer_name, v.vacancy_name, v.salary, v.vacancy_url
                    FROM vacancies v
                    INNER JOIN employers e USING (employer_id)
                    WHERE v.salary IS NOT NULL AND v.salary != 0
                    ORDER BY v.salary DESC

            """
        )

        return self.cur.fetchall()

    def get_avg_salary(self):
        """Функция для получения средней зарплаты по вакансиям."""

        self.cur.execute(
            """
                    SELECT AVG(salary)
                    FROM vacancies
            """
        )

        result = self.cur.fetchone()
        avg_salary = Decimal(result[0])
        formatted_avg_salary = format(avg_salary, ".2f")
        return formatted_avg_salary

    def get_vacancies_with_higher_salary(self):
        """Функция для получения списка всех вакансий,
        у которых зарплата выше средней по всем вакансиям."""

        avg_salary = self.get_avg_salary()[0][0]

        self.cur.execute(
            """
            SELECT v.vacancy_name, v.salary
            FROM vacancies v
            WHERE v.salary > %s
            """,
            (avg_salary,),
        )
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        """Функция для получения списка всех вакансий,
        в названии которых содержатся переданные в метод слова."""

        keyword = f"%{keyword.lower()}%"
        self.cur.execute(
            """
                    SELECT vacancy_name
                    FROM vacancies
                    WHERE vacancy_name LIKE %s
            """,
            (keyword,),
        )

        return self.cur.fetchall()

    def get_vacancies_with_average_salary(self):
        """
        Функция для получения списка всех вакансий,
        у которых зарплата выше средней по всем вакансиям.
        """

        query = """
        SELECT company_name, job_title, salary_from, salary_to, vacancy_url FROM vacancies
        WHERE currency = 'RUR' and salary_from > (SELECT AVG(salary_from) FROM vacancies)
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_vacancies_by_word(self, keyword):
        """
        Функция для получения списка всех вакансий,
        в названии которых содержатся переданные в метод слова, например: python.
        """

        query = """
        SELECT * FROM vacancies
        WHERE LOWER(job_title) LIKE %s
        """
        self.cur.execute(query, ("%" + keyword.lower() + "%",))
        return self.cur.fetchall()
