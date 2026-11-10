# Deterministic Ecto.Migration -> SQL translator (no deps). Usage: elixir ecto_sql_stub.exs <migration.exs>
# Emits SQL to stdout for the forward (up/change) direction.
defmodule Oban.Migrations do
  def up(_ \\ []), do: throw({:unsupported, "Oban.Migrations.up (needs oban dep)"})
end

defmodule StubRepo do
  def query!(sql, _params \\ []) do
    if String.contains?(sql, "SELECT EXISTS"), do: %{rows: [[false]], num_rows: 1, columns: []}, else: %{rows: [], num_rows: 0, columns: []}
  end
  def query(_sql, _params \\ []), do: {:ok, %{rows: [], num_rows: 0, columns: []}}
end

defmodule Ecto.Migration do
  defmacro __using__(_) do
    quote do
      import Ecto.Migration, except: [q: 1]
    end
  end

  defstruct [:name, :kind, :cols, :opts, :target, :unique, :where, :using, :check, :include, :concurrently]

  def repo, do: StubRepo
  def prefix, do: nil
  def q(i), do: "\"" <> to_string(i) <> "\""
  def table(n, opts \\ []), do: %{kind: :table, name: n, opts: opts}
  def index(t, cols, opts \\ []), do: %{kind: :index, table: tname(t), cols: List.wrap(cols), opts: opts}
  def unique_index(t, cols, opts \\ []), do: index(t, cols, Keyword.put(opts, :unique, true))
  def constraint(t, n, opts \\ []), do: %{kind: :constraint, table: tname(t), name: n, opts: opts}
  def fragment(s), do: {:fragment, s}
  def references(t, opts \\ []), do: {:ref, t, opts}
  def prefix_of(%{opts: o}), do: Keyword.get(o, :prefix, "public")
  defp tname(%{name: n}), do: n
  defp tname(n), do: n

  defp out(sql), do: IO.puts(String.trim_trailing(sql) <> ";")
  defp qt(t), do: q(prefix_of(t)) <> "." <> q(t.name)

  defp lit(nil), do: "NULL"
  defp lit({:fragment, s}), do: s
  defp lit(v) when is_binary(v), do: "'" <> String.replace(v, "'", "''") <> "'"
  defp lit(v) when is_boolean(v) or is_number(v), do: to_string(v)
  defp lit(v) when is_atom(v), do: lit(Atom.to_string(v))
  defp lit(v) when is_map(v) or is_list(v), do: "'" <> String.replace(jenc(v), "'", "''") <> "'"
  defp jenc(v) when is_map(v), do: "{" <> (v |> Enum.map(fn {k, x} -> "\"#{k}\":" <> jenc(x) end) |> Enum.join(",")) <> "}"
  defp jenc(v) when is_list(v), do: "[" <> (v |> Enum.map(&jenc/1) |> Enum.join(",")) <> "]"
  defp jenc(v) when is_binary(v), do: inspect(v)
  defp jenc(v), do: to_string(v)

  def type_sql({:array, t}), do: type_sql(t) <> "[]"
  def type_sql(:utc_datetime_usec), do: "timestamp(6) without time zone"
  def type_sql(:utc_datetime), do: "timestamp(0) without time zone"
  def type_sql(:naive_datetime), do: "timestamp(0) without time zone"
  def type_sql(:naive_datetime_usec), do: "timestamp(6) without time zone"
  def type_sql(:string), do: "varchar(255)"
  def type_sql(:binary_id), do: "uuid"
  def type_sql(:id), do: "bigint"
  def type_sql(:bigserial), do: "bigserial"
  def type_sql(:serial), do: "serial"
  def type_sql(:integer), do: "integer"
  def type_sql(:bigint), do: "bigint"
  def type_sql(:boolean), do: "boolean"
  def type_sql(:float), do: "double precision"
  def type_sql(:decimal), do: "numeric"
  def type_sql(:map), do: "jsonb"
  def type_sql(:binary), do: "bytea"
  def type_sql(:text), do: "text"
  def type_sql(:uuid), do: "uuid"
  def type_sql(:date), do: "date"
  def type_sql(:time), do: "time"
  def type_sql(:time_usec), do: "time(6)"
  def type_sql(:numeric), do: "numeric"
  def type_sql(:jsonb), do: "jsonb"
  def type_sql(:vector), do: "vector"
  def type_sql({:vector, n}), do: "vector(#{n})"
  def type_sql(a) when is_atom(a), do: Atom.to_string(a)
  def type_sql(b) when is_binary(b), do: b

  defp numeric_mod(t, o) do
    base = type_sql(t)
    cond do
      t in [:decimal, :numeric] and o[:precision] -> "numeric(#{o[:precision]},#{o[:scale] || 0})"
      t in [:string] and o[:size] -> "varchar(#{o[:size]})"
      true -> base
    end
  end

  defp ref_sql(t, o) do
    {tbl, pfx} = {t, Keyword.get(o, :prefix, "public")}
    col = Keyword.get(o, :column, :id)
    s = "REFERENCES #{q(pfx)}.#{q(tbl)}(#{q(col)})"
    s = if o[:with], do: s, else: s
    s = case o[:on_delete] do
      :delete_all -> s <> " ON DELETE CASCADE"
      :nilify_all -> s <> " ON DELETE SET NULL"
      :restrict -> s <> " ON DELETE RESTRICT"
      {:nilify, cols} -> s <> " ON DELETE SET NULL (#{Enum.map_join(cols, ",", &q/1)})"
      _ -> s
    end
    case o[:on_update] do
      :update_all -> s <> " ON UPDATE CASCADE"
      _ -> s
    end
  end

  defp col_def(name, type, o) do
    {tsql, refsql} = case type do
      {:ref, t, ro} -> {numeric_mod(Keyword.get(ro, :type, :bigint), ro), " " <> ref_name(name, t, ro) <> ref_sql(t, ro)}
      t -> {numeric_mod(t, o), ""}
    end
    pk = if o[:primary_key], do: " PRIMARY KEY", else: ""
    nn = if o[:null] == false, do: " NOT NULL", else: ""
    df = cond do
      Keyword.has_key?(o, :default) and match?({:array, _}, type) and o[:default] in ["[]", []] -> " DEFAULT '{}'"
      Keyword.has_key?(o, :default) and match?({:array, _}, type) and is_list(o[:default]) -> " DEFAULT ARRAY[" <> Enum.map_join(o[:default], ",", &lit/1) <> "]::" <> tsql
      Keyword.has_key?(o, :default) -> " DEFAULT " <> lit(o[:default])
      true -> ""
    end
    "#{q(name)} #{tsql}#{df}#{nn}#{pk}#{refsql}"
  end
  defp ref_name(_name, _t, ro) do
    case ro[:name] do
      nil -> ""
      n -> "CONSTRAINT #{q(n)} "
    end
  end
  # ref nullability lives in outer opts; reorder: type, NOT NULL after ref is valid in PG column defs
  # (column constraints may appear in any order)

  defp push(c), do: Process.put(:cols, [c | Process.get(:cols, [])])
  defp cols, do: Enum.reverse(Process.get(:cols, []))
  defp reset, do: Process.put(:cols, [])

  def add(name, type, opts \\ []), do: push({:add, name, type, opts})
  def add_if_not_exists(name, type, opts \\ []), do: push({:add_ine, name, type, opts})
  def modify(name, type, opts \\ []), do: push({:modify, name, type, opts})
  def remove(name), do: push({:remove, name})
  def remove(name, _type, _opts \\ []), do: push({:remove, name})
  def remove_if_exists(name, _t \\ nil), do: push({:remove_ie, name})
  def timestamps(opts \\ []) do
    t = Keyword.get(opts, :type, :naive_datetime)
    ins = Keyword.get(opts, :inserted_at, :inserted_at)
    upd = Keyword.get(opts, :updated_at, :updated_at)
    o = [null: false] ++ Keyword.take(opts, [:default])
    push({:add, ins, t, o}); push({:add, upd, t, o})
  end

  defmacro create(target, do: block) do
    quote do
      Ecto.Migration.reset_(); unquote(block); Ecto.Migration.do_create(unquote(target), false)
    end
  end
  defmacro create(target) do
    quote do: Ecto.Migration.do_create(unquote(target), false)
  end
  defmacro create_if_not_exists(target, do: block) do
    quote do
      Ecto.Migration.reset_(); unquote(block); Ecto.Migration.do_create(unquote(target), true)
    end
  end
  defmacro create_if_not_exists(target) do
    quote do: Ecto.Migration.do_create(unquote(target), true)
  end
  defmacro alter(target, do: block) do
    quote do
      Ecto.Migration.reset_(); unquote(block); Ecto.Migration.do_alter(unquote(target))
    end
  end
  def reset_, do: reset()

  def do_create(%{kind: :table} = t, ine) do
    cs = cols()
    pk_explicit = Enum.any?(cs, fn {:add, _, _, o} -> o[:primary_key] end)
    defs =
      (if t.opts[:primary_key] == false or pk_explicit, do: [], else: ["\"id\" bigserial PRIMARY KEY"]) ++
      Enum.map(cs, fn {:add, n, ty, o} -> col_def(n, ty, o) end)
    out("CREATE TABLE #{if ine, do: "IF NOT EXISTS "}#{qt(t)} (\n  #{Enum.join(defs, ",\n  ")}\n)")
    reset()
  end
  def do_create(%{kind: :index} = i, ine) do
    uq = if i.opts[:unique], do: "UNIQUE ", else: ""
    nm = i.opts[:name] || "#{i.table}_#{Enum.map_join(i.cols, "_", &to_string/1)}_#{if i.opts[:unique], do: "index", else: "index"}"
    cols = Enum.map_join(i.cols, ", ", fn c when is_atom(c) -> q(c); {:fragment, s} -> s; s when is_binary(s) -> s end)
    using = if i.opts[:using], do: " USING #{i.opts[:using]}", else: ""
    w = if i.opts[:where], do: " WHERE #{i.opts[:where]}", else: ""
    inc = if i.opts[:include], do: " INCLUDE (#{Enum.map_join(i.opts[:include], ", ", &q/1)})", else: ""
    out("CREATE #{uq}INDEX #{if ine, do: "IF NOT EXISTS "}#{q(nm)} ON #{q(i.opts[:prefix] || "public")}.#{q(i.table)}#{using} (#{cols})#{inc}#{w}")
  end
  def do_create(%{kind: :constraint} = c, _) do
    chk = if c.opts[:check], do: "CHECK (#{c.opts[:check]})", else: throw({:unsupported, "constraint without check: #{c.name}"})
    out("ALTER TABLE #{q(c.opts[:prefix] || "public")}.#{q(c.table)} ADD CONSTRAINT #{q(c.name)} #{chk}")
  end

  def do_alter(t) do
    Enum.each(cols(), fn
      {:add, n, ty, o} -> out("ALTER TABLE #{qt(t)} ADD COLUMN #{col_def(n, ty, o)}")
      {:add_ine, n, ty, o} -> out("ALTER TABLE #{qt(t)} ADD COLUMN IF NOT EXISTS #{col_def(n, ty, o)}")
      {:remove, n} -> out("ALTER TABLE #{qt(t)} DROP COLUMN #{q(n)}")
      {:remove_ie, n} -> out("ALTER TABLE #{qt(t)} DROP COLUMN IF EXISTS #{q(n)}")
      {:modify, n, ty, o} ->
        {tsql, ref} = case ty do
          {:ref, rt, ro} -> {numeric_mod(Keyword.get(ro, :type, :bigint), ro), ref_sql(rt, ro)}
          x -> {numeric_mod(x, o), nil}
        end
        out("ALTER TABLE #{qt(t)} ALTER COLUMN #{q(n)} TYPE #{tsql} USING #{q(n)}::#{tsql}")
        if o[:null] == false, do: out("ALTER TABLE #{qt(t)} ALTER COLUMN #{q(n)} SET NOT NULL")
        if o[:null] == true, do: out("ALTER TABLE #{qt(t)} ALTER COLUMN #{q(n)} DROP NOT NULL")
        if Keyword.has_key?(o, :default), do: out("ALTER TABLE #{qt(t)} ALTER COLUMN #{q(n)} SET DEFAULT #{lit(o[:default])}")
        if ref do
          cn = case ty do {:ref, _, ro} -> ro[:name] || "#{t.name}_#{n}_fkey" end
          out("ALTER TABLE #{qt(t)} DROP CONSTRAINT IF EXISTS #{q("#{t.name}_#{n}_fkey")}")
          out("ALTER TABLE #{qt(t)} ADD CONSTRAINT #{q(cn)} FOREIGN KEY (#{q(n)}) #{ref}")
        end
    end)
    reset()
  end

  def drop(%{kind: :table} = t), do: out("DROP TABLE #{qt(t)}")
  def drop(%{kind: :index} = i), do: out("DROP INDEX #{q(i.opts[:prefix] || "public")}.#{q(idx_name(i))}")
  def drop(%{kind: :constraint} = c), do: out("ALTER TABLE #{q(c.opts[:prefix] || "public")}.#{q(c.table)} DROP CONSTRAINT #{q(c.name)}")
  def drop_if_exists(%{kind: :table} = t), do: out("DROP TABLE IF EXISTS #{qt(t)}")
  def drop_if_exists(%{kind: :index} = i), do: out("DROP INDEX IF EXISTS #{q(i.opts[:prefix] || "public")}.#{q(idx_name(i))}")
  def drop_if_exists(%{kind: :constraint} = c), do: out("ALTER TABLE #{q(c.opts[:prefix] || "public")}.#{q(c.table)} DROP CONSTRAINT IF EXISTS #{q(c.name)}")
  defp idx_name(i), do: i.opts[:name] || "#{i.table}_#{Enum.map_join(i.cols, "_", &to_string/1)}_index"

  def rename(%{kind: :table} = t, to: n), do: out("ALTER TABLE #{qt(t)} RENAME TO #{q(n)}")
  def rename(%{kind: :table} = t, a, to: b), do: out("ALTER TABLE #{qt(t)} RENAME COLUMN #{q(a)} TO #{q(b)}")
  def execute(sql) when is_binary(sql), do: out(sql)
  def execute(f) when is_function(f, 0), do: out(f.())
  def execute(sql, _down) when is_binary(sql), do: out(sql)
  def flush, do: :ok
end

[file] = System.argv()
Code.compiler_options(ignore_module_conflict: true, ignore_already_consolidated: true)
try do
  mods = Code.compile_file(file)
  {mod, _} = List.last(mods)
  if function_exported?(mod, :up, 0), do: mod.up(), else: mod.change()
catch
  {:unsupported, why} -> IO.puts(:stderr, "UNSUPPORTED: " <> why); System.halt(3)
  kind, err -> IO.puts(:stderr, "TRANSLATE_ERROR: " <> Exception.format(kind, err, __STACKTRACE__) |> String.slice(0, 400)); System.halt(4)
end
