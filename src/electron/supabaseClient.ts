import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.error("Supabase environment variables are missing! Check your .env file.");
}
console.log("URL:", import.meta.env.VITE_SUPABASE_URL);
console.log("Key exists:", !!import.meta.env.VITE_SUPABASE_ANON_KEY);
export const supabase = createClient(supabaseUrl, supabaseKey);