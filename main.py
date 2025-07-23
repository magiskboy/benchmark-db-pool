import logging
from typing import List, cast
from contextlib import asynccontextmanager
from asyncpg.connection import os
from fastapi import FastAPI, Request, Query
from asyncpg import Connection, create_pool, Pool
from datetime import date
from pydantic import BaseModel, Field

logger = logging.getLogger('uvicorn')


@asynccontextmanager
async def lifespan(_):
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/postgres?options=-csearch_path%3Demployees')
    POOL_MIN_SIZE = int(os.getenv('DB_POOL_MIN_SIZE', '3'))
    POOL_MAX_SIZE = int(os.getenv('DB_POOL_MAX_SIZE', '10'))

    logger.info(f'POOL_MIN_SIZE: {POOL_MIN_SIZE}')
    logger.info(f'POOL_MAX_SIZE: {POOL_MAX_SIZE}')

    pool = await create_pool(
        DATABASE_URL,
        min_size=POOL_MIN_SIZE,
        max_size=POOL_MAX_SIZE,
    )

    yield {
        'db_pool': pool,
    }

    await pool.close()


app = FastAPI(lifespan=lifespan)


class Salary(BaseModel):
    employee_id: int = Field(alias='id')
    first_name: str = Field('')
    last_name: str = Field('')
    amount: int = Field(0)
    from_date: date = Field()
    to_date: date = Field()


class GetSalariesResponse(BaseModel):
    salaries: List[Salary] = Field([])


@app.get('/salaries', response_model=GetSalariesResponse)
async def get_salaries(r: Request, from_date: date = Query(example='1999-01-01'), to_date: date = Query(example='1999-06-01'), page: int = 0, page_size: int = 50):
    db_pool = cast(Pool, r.state.db_pool)

    async with db_pool.acquire() as conn:
        conn = cast(Connection, conn)
        sql = '''
            SELECT
              e.id,
              e.first_name,
              e.last_name,
              s.amount,
              s.from_date,
              s.to_date
            FROM
              salary s
              LEFT JOIN employee e ON s.employee_id = e.id
            WHERE
              s.from_date < $1 
              AND s.to_date > $2
            OFFSET $3
            LIMIT $4;
        '''

        async with conn.transaction():
            records = await conn.fetch(sql, from_date, to_date, page * page_size, page_size)

    data = {
        "salaries": [dict(item) for item in records]
    }

    return GetSalariesResponse.model_validate(data, by_alias=True)


class EmployeeInfo(BaseModel):
    employee_id: int = Field(alias='id')
    first_name: str = Field('')
    last_name: str = Field('')
    gender: str = Field('M')
    title: str = Field('')
    dept_id: str = Field('')
    dept_name: str = Field()


class GetEmployeesOfDepartments(BaseModel):
    employees: List[EmployeeInfo]


@app.get('/employees', response_model=GetEmployeesOfDepartments)
async def get_employees(r: Request, department_ids: List[str] = Query(example=['d004', 'd005']), page: int = 0, page_size: int = 50):
    db_pool = cast(Pool, r.state.db_pool)

    async with db_pool.acquire() as conn:
        conn = cast(Connection, conn)
        sql = '''
        SELECT
          e.id,
          e.first_name,
          e.last_name,
          e.gender,
          t.title,
          d.id as dept_id,
          d.dept_name
        FROM
          employee e
          JOIN title t ON e.id = t.employee_id
          JOIN department_employee de ON e.id = de.employee_id
          JOIN department d ON de.department_id = d.id
        where
        d.id = ANY($1)
        OFFSET
          $2
        LIMIT
          $3;
        '''
        async with conn.transaction():
            records = await conn.fetch(sql, department_ids, page * page_size, page_size)

    data = {
        "employees": [dict(item) for item in records]
    }

    return GetEmployeesOfDepartments.model_validate(data, by_alias=True)
