"""Enum types

Revision ID: 210f4111e8c5
Revises: ee37c81afa6e
Create Date: 2022-01-07 09:25:00.120009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '210f4111e8c5'
down_revision = 'ee37c81afa6e'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('underground', 'type', type_=sa.Integer(), existing_type=sa.Enum('OTHER', 'MINE', 'SHAFT', 'ADIT', 'PINGE', 'QUARRY', 'SHELTER', 'MILITARY_UNDERGROUND', 'URBAN_UNDERGROUND', 'MILL_RACE', 'DRAINAGE', 'TUNNEL', name='undergroundtype'), existing_nullable=False)
    op.alter_column('underground', 'state', type_=sa.Integer(), existing_type=sa.Enum('UNKNOWN', 'WORKING', 'MUSEUM', 'PRESERVED', 'NOT_BAD', 'BAD', 'DEMOLISHED', name='undergroundstate'), existing_nullable=False)
    op.alter_column('underground', 'accessibility', type_=sa.Integer(), existing_type=sa.Enum('INACCESSIBLE', 'WORKING', 'GUIDED_TOURS', 'GUARDED', 'LOCKED', 'FREELY_ACCESSIBLE', 'DIGGING_REQUIRED', name='undergroundaccessibility'), existing_nullable=True)
    op.alter_column('urbex', 'type', type_=sa.Integer(), existing_type=sa.Enum('OTHER', 'HOUSE', 'MANSION', 'RECREATION', 'ARMY', 'FACTORY', 'TECHNOLOGY', name='urbextype'), existing_nullable=False)
    op.alter_column('urbex', 'state', type_=sa.Integer(), existing_type=sa.Enum('UNKNOWN', 'LIKE_USED', 'FURNISHED', 'CLEANED_OUT', 'FALLING_APART', 'DEMOLISHED', 'UNDER_RESTORE', 'RESTORED', 'MUSEUM', name='urbexstate'), existing_nullable=False)
    op.alter_column('urbex', 'accessibility', type_=sa.Integer(), existing_type=sa.Enum('INACCESSIBLE', 'GUIDED_TOURS', 'GUARDED', 'MONITORED', 'FREELY_ACCESSIBLE', name='urbexaccessibility'), existing_nullable=True)
    op.alter_column('user', 'role', type_=sa.Integer(), existing_type=sa.Enum('ROOT', 'ADMIN', 'MODERATOR', 'CONTRIBUTOR', 'USER', 'NEWBIE', name='userrole'), existing_nullable=False)
    op.alter_column('event_log', 'type', type_=sa.Integer(), existing_type=sa.Enum('OTHER', 'CREATE', 'MODIFY', 'DELETE', name='eventtype'), existing_nullable=False)
    op.alter_column('event_log', 'severity', type_=sa.Integer(), existing_type=sa.Enum('LOW', 'NORMAL', 'HIGH', 'CRITICAL', name='eventseverity'), existing_nullable=False)
    op.alter_column('invitation', 'state', type_=sa.Integer(), existing_type=sa.Enum('WAITING', 'APPROVED', 'REGISTERED', 'TIMED_OUT', 'DENIED', name='invitationstate'), existing_nullable=False)
    op.alter_column('login_log', 'result', type_=sa.Integer(), existing_type=sa.Enum('SUCCESS', 'NOT_ACTIVE', 'BANNED', 'INVALID_PASSWORD', 'INVALID_EMAIL', name='loginresult'), existing_nullable=False)
    op.alter_column('material', 'type', type_=sa.Integer(), existing_type=sa.Enum('OTHER', 'COAL', 'LIGNITE', 'URANIUM', 'FIRE_CLAY', 'KAOLINITE', 'SAND', 'GRAPHITE', 'IRON', 'GOLD', 'COPPER', 'SILVER', 'TIN', 'SLATE', 'BARYTE', 'FLUORITE', 'FELDSPAR', name='materialtype'), existing_nullable=False)
    op.alter_column('upload', 'type', type_=sa.Integer(), existing_type=sa.Enum('OTHER', 'PHOTO', 'HISTORICAL_PHOTO', 'MAP', 'ARTICLE', 'BOOK', 'DOCUMENT', name='uploadtype'), existing_nullable=False)
    op.alter_column('location', 'country', type_=sa.Integer(), existing_type=sa.Enum('OTHER', 'CZECHIA', 'SLOVAKIA', 'POLAND', 'GERMANY', 'AUSTRIA', name='country'), existing_nullable=False)


def downgrade():
    op.alter_column('underground', 'type', existing_type=sa.Integer(), type_=sa.Enum('OTHER', 'MINE', 'SHAFT', 'ADIT', 'PINGE', 'QUARRY', 'SHELTER', 'MILITARY_UNDERGROUND', 'URBAN_UNDERGROUND', 'MILL_RACE', 'DRAINAGE', 'TUNNEL', name='undergroundtype'), existing_nullable=False)
    op.alter_column('underground', 'state', existing_type=sa.Integer(), type_=sa.Enum('UNKNOWN', 'WORKING', 'MUSEUM', 'PRESERVED', 'NOT_BAD', 'BAD', 'DEMOLISHED', name='undergroundstate'), existing_nullable=False)
    op.alter_column('underground', 'accessibility', existing_type=sa.Integer(), type_=sa.Enum('INACCESSIBLE', 'WORKING', 'GUIDED_TOURS', 'GUARDED', 'LOCKED', 'FREELY_ACCESSIBLE', 'DIGGING_REQUIRED', name='undergroundaccessibility'), existing_nullable=True)
    op.alter_column('urbex', 'type', existing_type=sa.Integer(), type_=sa.Enum('OTHER', 'HOUSE', 'MANSION', 'RECREATION', 'ARMY', 'FACTORY', 'TECHNOLOGY', name='urbextype'), existing_nullable=False)
    op.alter_column('urbex', 'state', existing_type=sa.Integer(), type_=sa.Enum('UNKNOWN', 'LIKE_USED', 'FURNISHED', 'CLEANED_OUT', 'FALLING_APART', 'DEMOLISHED', 'UNDER_RESTORE', 'RESTORED', 'MUSEUM', name='urbexstate'), existing_nullable=False)
    op.alter_column('urbex', 'accessibility', existing_type=sa.Integer(), type_=sa.Enum('INACCESSIBLE', 'GUIDED_TOURS', 'GUARDED', 'MONITORED', 'FREELY_ACCESSIBLE', name='urbexaccessibility'), existing_nullable=True)
    op.alter_column('user', 'role', existing_type=sa.Integer(), type_=sa.Enum('ROOT', 'ADMIN', 'MODERATOR', 'CONTRIBUTOR', 'USER', 'NEWBIE', name='userrole'), existing_nullable=False)
    op.alter_column('event_log', 'type', existing_type=sa.Integer(), type_=sa.Enum('OTHER', 'CREATE', 'MODIFY', 'DELETE', name='eventtype'), existing_nullable=False)
    op.alter_column('event_log', 'severity', existing_type=sa.Integer(), type_=sa.Enum('LOW', 'NORMAL', 'HIGH', 'CRITICAL', name='eventseverity'), existing_nullable=False)
    op.alter_column('invitation', 'state', existing_type=sa.Integer(), type_=sa.Enum('WAITING', 'APPROVED', 'REGISTERED', 'TIMED_OUT', 'DENIED', name='invitationstate'), existing_nullable=False)
    op.alter_column('login_log', 'result', existing_type=sa.Integer(), type_=sa.Enum('SUCCESS', 'NOT_ACTIVE', 'BANNED', 'INVALID_PASSWORD', 'INVALID_EMAIL', name='loginresult'), existing_nullable=False)
    op.alter_column('material', 'type', existing_type=sa.Integer(), type_=sa.Enum('OTHER', 'COAL', 'LIGNITE', 'URANIUM', 'FIRE_CLAY', 'KAOLINITE', 'SAND', 'GRAPHITE', 'IRON', 'GOLD', 'COPPER', 'SILVER', 'TIN', 'SLATE', 'BARYTE', 'FLUORITE', 'FELDSPAR', name='materialtype'), existing_nullable=False)
    op.alter_column('upload', 'type', existing_type=sa.Integer(), type_=sa.Enum('OTHER', 'PHOTO', 'HISTORICAL_PHOTO', 'MAP', 'ARTICLE', 'BOOK', 'DOCUMENT', name='uploadtype'), existing_nullable=False)
    op.alter_column('location', 'country', existing_type=sa.Integer(), type_=sa.Enum('OTHER', 'CZECHIA', 'SLOVAKIA', 'POLAND', 'GERMANY', 'AUSTRIA', name='country'), existing_nullable=False)
