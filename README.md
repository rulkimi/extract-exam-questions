1. Research PDF to Image
 - Upload pdf, and then converted to Image, baru analyse
2. Ensure extracted texts are accurate
3. Response format


4. Store data (JSON first, Firebase, Supabase, local??)
5. Frontend (upload, editable, save, output csv??)

create this table

create table documents (
  id uuid primary key default gen_random_uuid(),
  file_name text not null,
  file_url text not null,
  uploaded_date timestamp default now(),
  data JSONB,
  status text check (status IN ('in process', 'extracted', 'edited', 'failed')) default 'in process'
);
