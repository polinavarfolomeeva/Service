from aiogram import Router
from . import main_handlers, history_handlers, auth_handlers, catalog_handlers

main_router = Router()

main_router.include_router(catalog_handlers.router)
main_router.include_router(auth_handlers.router)
main_router.include_router(history_handlers.router)
main_router.include_router(main_handlers.router)