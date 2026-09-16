"use client";

import { useEffect, useMemo, useState } from "react";
import Image from "next/image";
import {
  BookOpen,
  BrainCircuit,
  CalendarClock,
  Check,
  Clipboard,
  Download,
  ExternalLink,
  FileText,
  Hash,
  LayoutDashboard,
  Lightbulb,
  Loader2,
  Moon,
  Newspaper,
  PenLine,
  RefreshCw,
  Send,
  Sparkles,
  Sun,
  TrendingUp
} from "lucide-react";
import { approveArticle, exportPost, generatePosts, getArticle, getArticles, getDashboard, getLinkedInStatus, publishPost, rewritePost, schedulePost, updatePost } from "@/lib/api";
import type { Article, DashboardStats, GeneratedPost, PostTone } from "@/lib/types";
import { Button } from "@/components/button";
import { cn } from "@/lib/utils";

const categories = ["AI", "Education", "Leadership", "Career", "Technology", "Business", "Hiring", "Workplace"];
const rewriteTones: PostTone[] = ["professional", "founder", "visionary", "short", "long", "storytelling"];

export default function Home() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [articles, setArticles] = useState<Article[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [selected, setSelected] = useState<Article | null>(null);
  const [activePostId, setActivePostId] = useState<number | null>(null);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dark, setDark] = useState(false);
  const [filter, setFilter] = useState("AI");
  const [linkedinConnected, setLinkedinConnected] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  useEffect(() => {
    void refresh();
    getLinkedInStatus().then((status) => setLinkedinConnected(status.connected)).catch(() => setLinkedinConnected(false));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    getArticle(selectedId).then((article) => {
      setSelected(article);
      const post = article.posts[0];
      setActivePostId(post?.id ?? null);
      setDraft(post?.body ?? "");
    });
  }, [selectedId]);

  const visibleArticles = useMemo(
    () => articles.filter((article) => filter === "AI" || article.category === filter || article.themes.includes(filter)),
    [articles, filter]
  );

  const activePost = selected?.posts.find((post) => post.id === activePostId) ?? selected?.posts[0] ?? null;

  async function refresh() {
    try {
      setError(null);
      const [nextStats, nextArticles] = await Promise.all([getDashboard(), getArticles()]);
      setStats(nextStats);
      setArticles(nextArticles);
      setSelectedId((current) => current ?? nextArticles[0]?.id ?? null);
    } catch (caught) {
      setError(readError(caught));
    }
  }

  async function handleGenerate() {
    if (!selected) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await approveArticle(selected.id);
      await generatePosts(selected.id, ["thought_leadership", "founder", "visionary"]);
      const updated = await getArticle(selected.id);
      setSelected(updated);
      setActivePostId(updated.posts[0]?.id ?? null);
      setDraft(updated.posts[0]?.body ?? "");
      await refresh();
      setNotice("Drafts generated.");
    } catch (caught) {
      setError(readError(caught));
    } finally {
      setBusy(false);
    }
  }

  async function handleRewrite(tone: PostTone) {
    if (!activePost) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const toneLabel = tone.replace("_", " ");
      const updatedBody = `${draft}\n\nRewrite direction: ${toneLabel}.`;
      const updated = await rewritePost(activePost.id, tone, updatedBody);
      setDraft(updated.body);
      replacePost(updated);
      setNotice(`Rewritten as ${toneLabel}.`);
    } catch (caught) {
      setError(readError(caught));
    } finally {
      setBusy(false);
    }
  }

  async function handleSchedule() {
    if (!activePost) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await saveActiveDraft();
      const scheduled = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
      const updated = await schedulePost(activePost.id, scheduled);
      replacePost(updated);
      await refresh();
      setNotice("Draft scheduled for tomorrow.");
    } catch (caught) {
      setError(readError(caught));
    } finally {
      setBusy(false);
    }
  }

  async function saveActiveDraft() {
    if (!activePost) return null;
    const updated = await updatePost(activePost.id, draft);
    replacePost(updated);
    return updated;
  }

  async function handleDownload(format: "linkedin" | "markdown" | "notion" | "word" | "pdf") {
    if (!activePost) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const saved = await saveActiveDraft();
      const blob = await exportPost(saved?.id ?? activePost.id, format);
      const extensions = { linkedin: "txt", markdown: "md", notion: "md", word: "doc", pdf: "pdf" };
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `linkedin-draft-${activePost.id}.${extensions[format]}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setNotice(`${formatLabel(format)} export downloaded.`);
    } catch (caught) {
      setError(readError(caught));
    } finally {
      setBusy(false);
    }
  }

  async function handleLinkedInExport() {
    if (!activePost) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await saveActiveDraft();
      await navigator.clipboard.writeText(draft);
      window.open("https://www.linkedin.com/feed/", "_blank", "noopener,noreferrer");
      setNotice("Draft copied. LinkedIn is opening so you can paste it into a new post.");
    } catch (caught) {
      setError(readError(caught));
    } finally {
      setBusy(false);
    }

  }

  async function handlePublish() {
    if (!activePost) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      const saved = await saveActiveDraft();
      const updated = await publishPost(saved?.id ?? activePost.id);
      replacePost(updated);
      await refresh();
      setNotice("Published to your LinkedIn profile.");
    } catch (caught) {
      setError(readError(caught));
    } finally {
      setBusy(false);
    }
  }

  function replacePost(updated: GeneratedPost) {
    setSelected((current) =>
      current
        ? { ...current, posts: current.posts.map((post) => (post.id === updated.id ? updated : post)) }
        : current
    );
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[248px_minmax(0,1fr)_320px]">
        <aside className="border-b border-border bg-panel px-4 py-4 lg:border-b-0 lg:border-r">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-accent">POSTPILOT</p>
              <h1 className="text-lg font-semibold">LinkedIn workspace</h1>
            </div>
            <Button variant="ghost" className="h-9 w-9 px-0" onClick={() => setDark((value) => !value)} title="Toggle theme">
              {dark ? <Sun size={17} /> : <Moon size={17} />}
            </Button>
          </div>

          <nav className="space-y-1">
            <SidebarItem icon={<LayoutDashboard size={17} />} label="Dashboard" active />
            <SidebarItem icon={<Newspaper size={17} />} label="News Queue" />
            <SidebarItem icon={<PenLine size={17} />} label="Saved Drafts" />
            <SidebarItem icon={<BookOpen size={17} />} label="Knowledge Base" />
          </nav>

          <div className="mt-8">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-foreground/55">Categories</p>
            <div className="space-y-1">
              {categories.map((category) => (
                <button
                  key={category}
                  className={cn(
                    "flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm hover:bg-muted",
                    filter === category && "bg-muted font-medium"
                  )}
                  onClick={() => setFilter(category)}
                >
                  {category}
                  <span className="text-xs text-foreground/50">
                    {articles.filter((article) => article.category === category || article.themes.includes(category)).length}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </aside>

        <section className="min-w-0">
          <div className="border-b border-border bg-panel/75 px-5 py-4 backdrop-blur">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
              <div>
                <p className="text-sm text-foreground/60">Your content workspace</p>
                <h2 className="text-2xl font-semibold">Discover ideas, write clearly, publish consistently</h2>
              </div>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                <Metric label="Today's Articles" value={stats?.todays_articles ?? 0} icon={<Newspaper size={16} />} />
                <Metric label="Awaiting Approval" value={stats?.awaiting_approval ?? 0} icon={<Check size={16} />} />
                <Metric label="Posts Generated" value={stats?.posts_generated ?? 0} icon={<Sparkles size={16} />} />
                <Metric label="AI Confidence" value={`${stats?.ai_confidence ?? 0}%`} icon={<BrainCircuit size={16} />} />
              </div>
            </div>
          </div>

          <div className="grid min-h-[calc(100vh-104px)] grid-cols-1 xl:grid-cols-[360px_minmax(0,1fr)]">
            <div className="border-b border-border bg-background p-4 xl:border-b-0 xl:border-r">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="font-semibold">High relevance articles</h3>
                <Button variant="ghost" className="h-8 w-8 px-0" onClick={() => void refresh()} title="Refresh">
                  <RefreshCw size={16} />
                </Button>
              </div>
              <div className="space-y-3">
                {visibleArticles.map((article) => (
                  <button
                    key={article.id}
                    onClick={() => setSelectedId(article.id)}
                    className={cn(
                      "w-full rounded-lg border border-border bg-panel p-3 text-left shadow-sm transition hover:border-accent",
                      selectedId === article.id && "border-accent"
                    )}
                  >
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <span className="rounded-md bg-muted px-2 py-1 text-xs">{article.category}</span>
                      <span className="text-sm font-semibold text-accent">{article.relevance_score}</span>
                    </div>
                    <h4 className="line-clamp-2 text-sm font-semibold leading-5">{article.title}</h4>
                    <p className="mt-2 line-clamp-2 text-xs leading-5 text-foreground/62">{article.summary}</p>
                    <div className="mt-3 flex items-center justify-between text-xs text-foreground/50">
                      <span>{article.source}</span>
                      <span>{article.status}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <article className="min-w-0 p-4 sm:p-6">
              {selected ? (
                <div className="mx-auto max-w-4xl space-y-6">
                  <div className="overflow-hidden rounded-lg border border-border bg-panel shadow-soft">
                    <div className="relative h-52 w-full bg-muted sm:h-72">
                      {selected.image_url ? (
                        <Image src={selected.image_url} alt="" fill className="object-cover" sizes="(max-width: 1024px) 100vw, 680px" />
                      ) : null}
                    </div>
                    <div className="p-5">
                      <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-foreground/60">
                        <span>{selected.source}</span>
                        <span>·</span>
                        <span>{selected.category}</span>
                        <span>·</span>
                        <a className="text-accent" href={selected.url} target="_blank" rel="noreferrer">
                          Open source
                        </a>
                      </div>
                      <h2 className="text-2xl font-semibold leading-tight">{selected.title}</h2>
                      <p className="mt-3 leading-7 text-foreground/70">{selected.summary}</p>
                    </div>
                  </div>

                  <InsightGrid selected={selected} />

                  <div className="rounded-lg border border-border bg-panel p-4">
                    <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <h3 className="font-semibold">Post studio</h3>
                        <p className="text-sm text-foreground/60">Generate several angles, edit your voice, then schedule or publish.</p>
                      </div>
                      <Button onClick={handleGenerate} disabled={busy}>
                        {busy ? <Loader2 className="animate-spin" size={16} /> : <Sparkles size={16} />}
                        Generate
                      </Button>
                    </div>

                    {error ? <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}
                    {notice ? <div className="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">{notice}</div> : null}

                    {selected.posts.length > 0 ? (
                      <div className="space-y-4">
                        <div className="flex flex-wrap gap-2">
                          {selected.posts.map((post) => (
                            <Button
                              key={post.id}
                              variant={activePostId === post.id ? "primary" : "secondary"}
                              onClick={() => {
                                setActivePostId(post.id);
                                setDraft(post.body);
                              }}
                            >
                              Version {post.version}
                            </Button>
                          ))}
                        </div>
                        <textarea
                          className="min-h-80 w-full resize-y rounded-md border border-border bg-background p-4 text-sm leading-6 outline-none focus:border-accent"
                          value={draft}
                          onChange={(event) => setDraft(event.target.value)}
                        />
                        <div className="flex flex-wrap gap-2">
                          {rewriteTones.map((tone) => (
                            <Button key={tone} variant="secondary" onClick={() => handleRewrite(tone)} disabled={busy}>
                              <PenLine size={15} />
                              {tone.replace("_", " ")}
                            </Button>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="rounded-md border border-dashed border-border p-8 text-center text-sm text-foreground/60">
                        Select Generate to create thought leadership, founder, and visionary drafts.
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="rounded-lg border border-border bg-panel p-10 text-center">Loading workspace...</div>
              )}
            </article>
          </div>
        </section>

        <aside className="border-t border-border bg-panel px-4 py-5 lg:border-l lg:border-t-0">
          <h3 className="mb-4 font-semibold">Publishing controls</h3>
          <Score label="Relevance" value={selected?.relevance_score ?? 0} />
          <Score label="Virality" value={selected?.virality_score ?? 0} />
          <Score label="AI Confidence" value={selected?.ai_confidence ?? 0} />

          <div className="mt-6">
            <p className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <TrendingUp size={16} />
              Trending topics
            </p>
            <div className="flex flex-wrap gap-2">
              {(stats?.trending_topics ?? []).map((topic) => (
                <span key={topic} className="rounded-md border border-border px-2 py-1 text-xs">
                  {topic}
                </span>
              ))}
            </div>
          </div>

          <div className="mt-6">
            <p className="mb-2 flex items-center gap-2 text-sm font-semibold">
              <Hash size={16} />
              Suggested hashtags
            </p>
            <p className="text-sm leading-6 text-foreground/70">{selected?.hashtags}</p>
          </div>

          <div className="mt-6 space-y-2">
            <Button className="w-full" variant={linkedinConnected ? "secondary" : "primary"} onClick={() => window.location.href = `${process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api"}/linkedin/connect`}>
              <Send size={16} />
              {linkedinConnected ? "LinkedIn connected" : "Connect LinkedIn"}
            </Button>
            <Button className="w-full" onClick={handleSchedule} disabled={!activePost || busy}>
              <CalendarClock size={16} />
              Schedule Tomorrow
            </Button>
            <Button variant="secondary" className="w-full" onClick={handleLinkedInExport} disabled={!activePost || busy}>
              <Send size={16} />
              Export to LinkedIn
            </Button>
            <Button variant="secondary" className="w-full" onClick={handlePublish} disabled={!activePost || busy || !linkedinConnected}>
              <Send size={16} />
              Publish now
            </Button>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="secondary" className="w-full px-2" onClick={() => handleDownload("markdown")} disabled={!activePost || busy}>
                <Download size={15} />
                Markdown
              </Button>
              <Button variant="secondary" className="w-full px-2" onClick={() => handleDownload("notion")} disabled={!activePost || busy}>
                <Clipboard size={15} />
                Notion
              </Button>
              <Button variant="secondary" className="w-full px-2" onClick={() => handleDownload("word")} disabled={!activePost || busy}>
                <FileText size={15} />
                Word
              </Button>
              <Button variant="secondary" className="w-full px-2" onClick={() => handleDownload("pdf")} disabled={!activePost || busy}>
                <ExternalLink size={15} />
                PDF
              </Button>
            </div>
          </div>

          {activePost ? (
            <div className="mt-6 rounded-lg border border-border bg-background p-3 text-xs leading-5 text-foreground/60">
              <strong className="text-foreground">Draft status:</strong> {activePost.status}
              {activePost.scheduled_for ? <div>Scheduled for {new Date(activePost.scheduled_for).toLocaleString()}</div> : null}
            </div>
          ) : null}
        </aside>
      </div>
    </main>
  );
}

function readError(caught: unknown) {
  if (caught instanceof Error) return caught.message;
  return "Something went wrong. Check that the backend is running on http://localhost:8000.";
}

function formatLabel(format: "linkedin" | "markdown" | "notion" | "word" | "pdf") {
  return format === "pdf" ? "PDF" : format === "word" ? "Word" : format === "notion" ? "Notion" : format === "linkedin" ? "LinkedIn" : "Markdown";
}

function SidebarItem({ icon, label, active = false }: { icon: React.ReactNode; label: string; active?: boolean }) {
  return (
    <button className={cn("flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-muted", active && "bg-muted font-medium")}>
      {icon}
      {label}
    </button>
  );
}

function Metric({ label, value, icon }: { label: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="min-w-32 rounded-lg border border-border bg-background px-3 py-2">
      <div className="mb-1 flex items-center gap-2 text-xs text-foreground/55">{icon}{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}

function Score({ label, value }: { label: string; value: number }) {
  return (
    <div className="mb-4">
      <div className="mb-1 flex justify-between text-sm">
        <span>{label}</span>
        <span className="font-semibold">{value}</span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div className="h-2 rounded-full bg-accent" style={{ width: `${Math.min(value, 100)}%` }} />
      </div>
    </div>
  );
}

function InsightGrid({ selected }: { selected: Article }) {
  const items = [
    { title: "AI Analysis", body: selected.analysis, icon: <BrainCircuit size={17} /> },
    { title: "Key Takeaways", body: selected.key_takeaways, icon: <FileText size={17} /> },
    { title: "Your angle", body: selected.personal_angle, icon: <Sparkles size={17} /> },
    { title: "Founder Opinion", body: selected.founder_opinion, icon: <Lightbulb size={17} /> }
  ];
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {items.map((item) => (
        <section key={item.title} className="rounded-lg border border-border bg-panel p-4">
          <h3 className="mb-2 flex items-center gap-2 font-semibold">
            {item.icon}
            {item.title}
          </h3>
          <p className="text-sm leading-6 text-foreground/68">{item.body}</p>
        </section>
      ))}
    </div>
  );
}
