-- ============================================================
-- Facial Clinic CRM - Database Schema
-- הרץ קובץ זה ב-Supabase Dashboard -> SQL Editor -> New Query
-- ============================================================

-- הפעלת UUID extension (בד"כ כבר פעיל ב-Supabase, אבל ליתר ביטחון)
create extension if not exists "uuid-ossp";

-- ============================================================
-- טבלת לקוחות
-- ============================================================
create table if not exists clients (
    id uuid primary key default uuid_generate_v4(),
    full_name text not null,
    phone text not null,
    email text,
    date_of_birth date,
    skin_type text,
    allergies text,
    medical_notes text,
    referral_source text,
    general_notes text,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_clients_full_name on clients (full_name);
create index if not exists idx_clients_phone on clients (phone);

-- ============================================================
-- טבלת תורים (יומן)
-- ============================================================
create table if not exists appointments (
    id uuid primary key default uuid_generate_v4(),
    client_id uuid not null references clients (id) on delete cascade,
    treatment_name text not null,
    start_time timestamptz not null,
    end_time timestamptz not null,
    price numeric(10, 2),
    status text not null default 'scheduled'
        check (status in ('scheduled', 'confirmed', 'completed', 'cancelled', 'no_show')),
    notes text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_appointments_client_id on appointments (client_id);
create index if not exists idx_appointments_start_time on appointments (start_time);

-- ============================================================
-- טבלת תשלומים
-- ============================================================
create table if not exists payments (
    id uuid primary key default uuid_generate_v4(),
    client_id uuid not null references clients (id) on delete cascade,
    appointment_id uuid references appointments (id) on delete set null,
    amount numeric(10, 2) not null check (amount > 0),
    method text not null default 'cash'
        check (method in ('cash', 'credit_card', 'bit', 'bank_transfer', 'other')),
    paid_at timestamptz not null,
    notes text,
    created_at timestamptz not null default now()
);

create index if not exists idx_payments_client_id on payments (client_id);
create index if not exists idx_payments_appointment_id on payments (appointment_id);

-- ============================================================
-- טבלת תמונות לקוחות (מטא-דאטה; הקבצים עצמם ב-Storage)
-- ============================================================
create table if not exists client_photos (
    id uuid primary key default uuid_generate_v4(),
    client_id uuid not null references clients (id) on delete cascade,
    appointment_id uuid references appointments (id) on delete set null,
    storage_path text not null,
    caption text,
    taken_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists idx_client_photos_client_id on client_photos (client_id);

-- ============================================================
-- טריגר לעדכון אוטומטי של updated_at
-- ============================================================
create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists set_updated_at_clients on clients;
create trigger set_updated_at_clients
    before update on clients
    for each row execute function update_updated_at_column();

drop trigger if exists set_updated_at_appointments on appointments;
create trigger set_updated_at_appointments
    before update on appointments
    for each row execute function update_updated_at_column();

-- ============================================================
-- הערה לגבי Row Level Security (RLS):
-- בשלב זה (שלב 1, שרת לוקאלי עם Service Role Key) אנחנו לא מפעילים RLS,
-- כיוון שהשרת שלנו עוקף אותו עם ה-Service Role Key בכל מקרה.
-- כשנעבור לפרודקשן/ענן ונחשוף את ה-frontend ישירות מול Supabase,
-- נצטרך להפעיל RLS ולהגדיר policies מתאימות. נטפל בזה בשלב מתקדם יותר.
-- ============================================================
