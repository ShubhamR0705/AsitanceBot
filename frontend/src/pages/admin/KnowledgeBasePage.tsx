import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { adminApi } from "../../api/client";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { EmptyState } from "../../components/ui/EmptyState";
import { Input, Textarea } from "../../components/ui/Input";
import { PageTransition } from "../../components/ui/PageTransition";
import { Skeleton } from "../../components/ui/Skeleton";

export function KnowledgeBasePage() {
  const queryClient = useQueryClient();
  const kb = useQuery({ queryKey: ["knowledge-base"], queryFn: adminApi.knowledgeBase });
  const [form, setForm] = useState({
    category: "",
    title: "",
    content: "",
    keywords: "",
    is_active: true
  });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const create = useMutation({
    mutationFn: () => adminApi.createKnowledgeBaseEntry(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-base"] });
      setForm({ category: "", title: "", content: "", keywords: "", is_active: true });
      setEditingId(null);
      setError("");
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Unable to create entry")
  });
  const update = useMutation({
    mutationFn: () => {
      if (!editingId) throw new Error("No entry selected");
      return adminApi.updateKnowledgeBaseEntry(editingId, form);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-base"] });
      setForm({ category: "", title: "", content: "", keywords: "", is_active: true });
      setEditingId(null);
      setError("");
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Unable to update entry")
  });
  const remove = useMutation({
    mutationFn: adminApi.deleteKnowledgeBaseEntry,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["knowledge-base"] }),
    onError: (err) => setError(err instanceof Error ? err.message : "Unable to delete entry")
  });
  const toggleActive = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) => adminApi.updateKnowledgeBaseEntry(id, { is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["knowledge-base"] }),
    onError: (err) => setError(err instanceof Error ? err.message : "Unable to update entry")
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (editingId) update.mutate();
    else create.mutate();
  };

  return (
    <PageTransition>
      <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
        <section className="space-y-5">
          <div>
            <h2 className="text-2xl font-semibold text-ink">Knowledge base</h2>
            <p className="mt-2 text-sm text-muted">Approved content used by AI troubleshooting responses.</p>
          </div>
          {kb.isLoading ? (
            <Skeleton className="h-96" />
          ) : kb.data?.length ? (
            <div className="grid gap-4 md:grid-cols-2">
              {kb.data.map((entry) => (
                <article key={entry.id} className="rounded-lg border border-line bg-surface p-5 shadow-soft">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <Badge tone="brand">{entry.category.replaceAll("_", " ")}</Badge>
                    <Badge tone={entry.is_active ? "success" : "neutral"}>{entry.is_active ? "Active" : "Inactive"}</Badge>
                  </div>
                  <h3 className="text-base font-semibold text-ink">{entry.title}</h3>
                  <p className="mt-3 line-clamp-4 text-sm leading-6 text-muted">{entry.content}</p>
                  <p className="mt-4 text-xs text-muted">Keywords: {entry.keywords}</p>
                  <p className="mt-1 text-xs text-muted">Shown {entry.usage_count} times · Updated {new Date(entry.updated_at).toLocaleString()}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => {
                        setEditingId(entry.id);
                        setForm({
                          category: entry.category,
                          title: entry.title,
                          content: entry.content,
                          keywords: entry.keywords,
                          is_active: entry.is_active
                        });
                      }}
                    >
                      Edit
                    </Button>
                    <Button type="button" variant="ghost" onClick={() => toggleActive.mutate({ id: entry.id, is_active: !entry.is_active })}>
                      {entry.is_active ? "Disable" : "Enable"}
                    </Button>
                    <Button type="button" variant="danger" onClick={() => remove.mutate(entry.id)}>
                      Delete
                    </Button>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <EmptyState title="No KB entries" description="Create the first approved troubleshooting entry." />
          )}
        </section>

        <form onSubmit={submit} className="h-fit rounded-lg border border-line bg-surface p-5 shadow-soft">
          <h3 className="text-lg font-semibold text-ink">{editingId ? "Edit KB entry" : "New KB entry"}</h3>
          <label className="mt-5 block">
            <span className="mb-2 block text-sm font-medium text-ink">Category</span>
            <Input value={form.category} onChange={(event) => setForm((current) => ({ ...current, category: event.target.value }))} placeholder="VPN" required />
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink">Title</span>
            <Input value={form.title} onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))} required />
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink">Content</span>
            <Textarea value={form.content} onChange={(event) => setForm((current) => ({ ...current, content: event.target.value }))} required />
          </label>
          <label className="mt-4 block">
            <span className="mb-2 block text-sm font-medium text-ink">Keywords</span>
            <Input value={form.keywords} onChange={(event) => setForm((current) => ({ ...current, keywords: event.target.value }))} placeholder="vpn,gateway,mfa" required />
          </label>
          <label className="mt-4 flex items-center gap-2 text-sm text-ink">
            <input type="checkbox" checked={form.is_active} onChange={(event) => setForm((current) => ({ ...current, is_active: event.target.checked }))} />
            Active
          </label>
          {error ? <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
          <Button type="submit" isLoading={create.isPending || update.isPending} className="mt-5 w-full">
            {editingId ? "Save entry" : "Add entry"}
          </Button>
          {editingId ? (
            <Button
              type="button"
              variant="ghost"
              className="mt-2 w-full"
              onClick={() => {
                setEditingId(null);
                setForm({ category: "", title: "", content: "", keywords: "", is_active: true });
              }}
            >
              Cancel edit
            </Button>
          ) : null}
        </form>
      </div>
    </PageTransition>
  );
}
