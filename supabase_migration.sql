-- Run this in your Supabase SQL Editor (or as a migration file)

create table if not exists public.discord_messages (
    id               bigint        generated always as identity primary key,
    channel_name     text          not null,
    user_id          text          not null,
    message_content  text          not null default '',
    timestamp        timestamptz   not null default now()
);

-- Index for fast filtering by channel
create index if not exists idx_discord_messages_channel
    on public.discord_messages (channel_name);

-- Index for fast filtering by user
create index if not exists idx_discord_messages_user
    on public.discord_messages (user_id);

-- Optional: enable Row Level Security and allow only your service-role key to insert
alter table public.discord_messages enable row level security;

create policy "Service role can insert"
    on public.discord_messages
    for insert
    to service_role         -- use your anon/service key accordingly
    with check (true);

create policy "Service role can select"
    on public.discord_messages
    for select
    to service_role
    using (true);
