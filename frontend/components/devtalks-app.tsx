"use client";

import {
  ArrowDownWideNarrow,
  ArrowRight,
  Bookmark,
  Code2,
  Compass,
  Flame,
  Heart,
  Home,
  LogOut,
  MessageCircle,
  Moon,
  Plus,
  Search,
  Settings2,
  Sparkles,
  Sun,
  Users,
  X,
} from "lucide-react";
import {
  FormEvent,
  PointerEvent as ReactPointerEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";
import {
  AuthDialog,
  CommentsDialog,
  PostComposerDialog,
  ProfileDialog,
} from "@/components/dialogs";
import { Avatar, PostCard } from "@/components/post-card";
import { api, clearSession, hasSession } from "@/lib/api";
import type {
  Category,
  FeedType,
  Post,
  Tag,
  User,
  UserBrief,
} from "@/types/api";

type View = "feed" | "explore" | "bookmarks" | "profile";
type SearchMode = "posts" | "developers";

type Theme = "light" | "dark";
const THEME_CHANGE_EVENT = "devtalks-theme-change";

function getThemeSnapshot(): Theme {
  const savedTheme = window.localStorage.getItem("devtalks.theme");
  if (savedTheme === "light" || savedTheme === "dark") return savedTheme;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function subscribeToThemeChange(onChange: () => void) {
  window.addEventListener("storage", onChange);
  window.addEventListener(THEME_CHANGE_EVENT, onChange);
  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener(THEME_CHANGE_EVENT, onChange);
  };
}

function setThemePreference(theme: Theme) {
  window.localStorage.setItem("devtalks.theme", theme);
  window.dispatchEvent(new Event(THEME_CHANGE_EVENT));
}

function getServerThemeSnapshot(): Theme {
  return "light";
}

const feedLabels: Record<FeedType, string> = {
  new: "Новые",
  top: "Популярное",
  hot: "Обсуждают",
};

function PageControls({
  page,
  pages,
  onChange,
}: {
  page: number;
  pages: number;
  onChange: (page: number) => void;
}) {
  if (pages <= 1) return null;
  return (
    <div className="pagination">
      <button disabled={page <= 1} onClick={() => onChange(page - 1)}>
        ← Назад
      </button>
      <span>{page} <i /> {pages}</span>
      <button disabled={page >= pages} onClick={() => onChange(page + 1)}>
        Дальше →
      </button>
    </div>
  );
}

function DeveloperCard({ user }: { user: UserBrief }) {
  return (
    <article className="developer-card">
      <Avatar username={user.username} image={user.avatar_url} size="large" />
      <div className="developer-card-info">
        <strong>@{user.username}</strong>
        <span><Sparkles size={13} /> {user.karma} karma</span>
      </div>
      <span className="developer-role">Разработчик DevTalks</span>
    </article>
  );
}

export function DevTalksApp() {
  const [view, setView] = useState<View>("feed");
  const [feedType, setFeedType] = useState<FeedType>("new");
  const [searchMode, setSearchMode] = useState<SearchMode>("posts");
  const [searchDraft, setSearchDraft] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const [categoryId, setCategoryId] = useState<number | undefined>();
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [posts, setPosts] = useState<Post[]>([]);
  const [developers, setDevelopers] = useState<UserBrief[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [loadedKey, setLoadedKey] = useState("");
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const [refreshCounter, setRefreshCounter] = useState(0);
  const [authMode, setAuthMode] = useState<"login" | "register" | null>(null);
  const [editingPost, setEditingPost] = useState<Post | null | "new">(null);
  const [commentsPost, setCommentsPost] = useState<Post | null>(null);
  const [editingProfile, setEditingProfile] = useState(false);
  const theme = useSyncExternalStore(
    subscribeToThemeChange,
    getThemeSnapshot,
    getServerThemeSnapshot,
  );
  const searchInputRef = useRef<HTMLInputElement>(null);

  const refresh = useCallback(() => setRefreshCounter((value) => value + 1), []);
  function moveHeroScene(event: ReactPointerEvent<HTMLElement>) {
    if (event.pointerType === "touch") return;
    const bounds = event.currentTarget.getBoundingClientRect();
    const x = (event.clientX - bounds.left) / bounds.width - 0.5;
    const y = (event.clientY - bounds.top) / bounds.height - 0.5;
    event.currentTarget.style.setProperty("--hero-rotate-x", `${-y * 9}deg`);
    event.currentTarget.style.setProperty("--hero-rotate-y", `${x * 12}deg`);
  }

  function resetHeroScene(event: ReactPointerEvent<HTMLElement>) {
    event.currentTarget.style.setProperty("--hero-rotate-x", "0deg");
    event.currentTarget.style.setProperty("--hero-rotate-y", "0deg");
  }

  const loadKey = [
    view,
    feedType,
    searchMode,
    appliedSearch,
    categoryId ?? "",
    page,
    user?.id ?? "",
    refreshCounter,
  ].join(":");
  const loading = loadedKey !== loadKey;

  useEffect(() => {
    if (hasSession()) {
      void api.me().then(setUser).catch((reason: unknown) => {
        clearSession();
        setToast(
          reason instanceof Error
            ? `Сессия завершена: ${reason.message}`
            : "Не удалось восстановить сессию.",
        );
      });
    }

    const slug = new URLSearchParams(window.location.search).get("post");
    if (slug) {
      void api.postBySlug(slug)
        .then(setCommentsPost)
        .catch((reason: unknown) => {
          setToast(reason instanceof Error ? reason.message : "Публикация не найдена.");
        });
    }
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(() => setToast(""), 4200);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  useEffect(() => {
    let active = true;
    void api.categories()
      .then((result) => {
        if (active) setCategories(result);
      })
      .catch((reason: unknown) => {
        if (active) setToast(reason instanceof Error ? reason.message : "Не удалось загрузить темы.");
      });
    void api.tags()
      .then((result) => {
        if (active) setTags(result.items);
      })
      .catch((reason: unknown) => {
        if (active) setToast(reason instanceof Error ? reason.message : "Не удалось загрузить теги.");
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function load() {
      await Promise.resolve();
      if (view === "bookmarks") {
        if (!user) {
          if (active) {
            setPosts([]);
            setDevelopers([]);
            setTotal(0);
            setPages(1);
            setError("Войди в аккаунт, чтобы увидеть сохранённые публикации.");
            setLoadedKey(loadKey);
          }
          return;
        }
        const result = await api.bookmarks(page, 10);
        if (active) {
          setPosts(result.items);
          setDevelopers([]);
          setTotal(result.total);
          setPages(Math.max(result.pages, 1));
          setError("");
          setLoadedKey(loadKey);
        }
      } else if (view === "profile") {
        if (!user) {
          if (active) {
            setPosts([]);
            setDevelopers([]);
            setTotal(0);
            setPages(1);
            setError("Войди в аккаунт, чтобы открыть свой профиль.");
            setLoadedKey(loadKey);
          }
          return;
        }
        const result = await api.userPosts(user.id, page, 10);
        if (active) {
          setPosts(result.items);
          setDevelopers([]);
          setTotal(result.total);
          setPages(Math.max(result.pages, 1));
          setError("");
          setLoadedKey(loadKey);
        }
      } else if (view === "explore" && searchMode === "developers") {
        const result = await api.users(appliedSearch, page, 20);
        if (active) {
          setDevelopers(result.items);
          setPosts([]);
          setTotal(result.total);
          setPages(Math.max(result.pages, 1));
          setError("");
          setLoadedKey(loadKey);
        }
        return;
      } else if (appliedSearch || categoryId) {
        const result = await api.posts({
          q: appliedSearch || undefined,
          category_id: categoryId,
          page,
          size: 10,
        });
        if (active) {
          setPosts(result.items);
          setDevelopers([]);
          setTotal(result.total);
          setPages(Math.max(result.pages, 1));
          setError("");
          setLoadedKey(loadKey);
        }
      } else {
        const result = await api.feed(feedType, page, 10);
        if (active) {
          setPosts(result.items);
          setDevelopers([]);
          setTotal(result.total);
          setPages(Math.max(result.pages, 1));
          setError("");
          setLoadedKey(loadKey);
        }
      }
    }

    void load()
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof Error ? reason.message : "Не удалось загрузить данные.");
          setPosts([]);
          setDevelopers([]);
          setLoadedKey(loadKey);
        }
      });
    return () => {
      active = false;
    };
  }, [
    view,
    feedType,
    searchMode,
    appliedSearch,
    categoryId,
    page,
    user,
    refreshCounter,
    loadKey,
  ]);

  const authors = useMemo(() => {
    const unique = new Map<number, UserBrief>();
    for (const post of posts) unique.set(post.author.id, post.author);
    return Array.from(unique.values()).slice(0, 4);
  }, [posts]);

  function navigate(nextView: View) {
    setView(nextView);
    setPage(1);
    if (nextView !== "explore") {
      setAppliedSearch("");
      setSearchDraft("");
      setCategoryId(undefined);
    }
  }

  function chooseCategory(id?: number) {
    setCategoryId(id);
    setPage(1);
    setAppliedSearch("");
    setSearchDraft("");
    setView("feed");
  }

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPage(1);
    setCategoryId(undefined);
    setAppliedSearch(searchDraft.trim());
    setView("explore");
    searchInputRef.current?.blur();
  }

  function onAuthenticated(profile: User) {
    setUser(profile);
    setAuthMode(null);
    setToast(`Рады видеть, @${profile.username}!`);
    refresh();
  }

  function logout() {
    clearSession();
    setUser(null);
    setView("feed");
    setToast("Ты вышел из аккаунта.");
    refresh();
  }

  async function savePost(body: Parameters<typeof api.createPost>[0]) {
    if (editingPost && editingPost !== "new") {
      await api.updatePost(editingPost.id, body);
      setToast("Изменения сохранены.");
    } else {
      await api.createPost(body);
      setToast("Публикация отправлена в ленту.");
    }
    setEditingPost(null);
    setView("feed");
    setPage(1);
    refresh();
  }

  async function vote(post: Post) {
    try {
      await api.vote(post.id, post.user_vote !== null);
      refresh();
      if (user?.id === post.author.id) {
        try {
          setUser(await api.me());
        } catch (reason) {
          setToast(
            reason instanceof Error
              ? `Голос сохранён, но не удалось обновить профиль: ${reason.message}`
              : "Голос сохранён, но не удалось обновить профиль.",
          );
        }
      }
    } catch (reason) {
      setToast(reason instanceof Error ? reason.message : "Не удалось изменить голос.");
    }
  }

  async function bookmark(post: Post) {
    try {
      await api.bookmark(post.id, post.is_bookmarked);
      setToast(post.is_bookmarked ? "Удалено из закладок." : "Сохранено в закладки.");
      refresh();
    } catch (reason) {
      setToast(reason instanceof Error ? reason.message : "Не удалось сохранить публикацию.");
    }
  }

  async function deletePost(post: Post) {
    if (!window.confirm("Удалить публикацию? Это действие нельзя отменить.")) return;
    try {
      await api.deletePost(post.id);
      setToast("Публикация удалена.");
      refresh();
    } catch (reason) {
      setToast(reason instanceof Error ? reason.message : "Не удалось удалить публикацию.");
    }
  }

  async function saveProfile(profile: User) {
    setUser(profile);
    setEditingProfile(false);
    setToast("Профиль обновлён.");
    refresh();
  }

  async function uploadAvatar(file: File) {
    const profile = await api.uploadAvatar(file);
    setUser(profile);
    setToast("Фото профиля обновлено.");
    refresh();
    return profile;
  }

  async function removeAvatar() {
    const profile = await api.removeAvatar();
    setUser(profile);
    setToast("Фото профиля удалено.");
    refresh();
    return profile;
  }

  const currentTitle =
    view === "bookmarks"
      ? "Сохранённое"
      : view === "profile"
        ? "Мои публикации"
        : view === "explore"
          ? "Исследуй сообщество"
          : categoryId
            ? categories.find((item) => item.id === categoryId)?.name ?? "Лента"
            : "Лента";

  return (
    <main className="app-shell">
      <header className="topbar">
        <button className="brand brand-button" onClick={() => navigate("feed")} aria-label="DevTalks — главная">
          <span className="brand-mark"><Code2 size={21} /></span>
          <span>devtalks<span className="brand-period">.</span></span>
        </button>
        <form className={`top-search ${searchOpen ? "top-search-open" : ""}`} onSubmit={submitSearch}>
          <Search size={17} />
          <input
            ref={searchInputRef}
            value={searchDraft}
            onChange={(event) => setSearchDraft(event.target.value)}
            placeholder={searchMode === "posts" ? "Найти статью, тему..." : "Найти разработчика..."}
            aria-label="Поиск по DevTalks"
          />
          <button type="submit" className="search-submit">Найти</button>
          <button type="button" className="search-close" onClick={() => setSearchOpen(false)} aria-label="Закрыть поиск"><X size={17} /></button>
        </form>
        <div className="topbar-actions">
          <button
            className="icon-button mobile-search-toggle"
            onClick={() => {
              setSearchOpen((open) => !open);
              window.setTimeout(() => searchInputRef.current?.focus(), 0);
            }}
            aria-label="Открыть поиск"
          >
            <Search size={19} />
          </button>
          <button
            className="icon-button theme-toggle"
            onClick={() => setThemePreference(theme === "light" ? "dark" : "light")}
            aria-label={theme === "light" ? "Включить тёмную тему" : "Включить светлую тему"}
            title={theme === "light" ? "Тёмная тема" : "Светлая тема"}
          >
            {theme === "light" ? <Moon size={18} /> : <Sun size={18} />}
          </button>
          {user ? (
            <button className="account-chip" onClick={logout} title="Выйти из аккаунта">
              <Avatar username={user.username} image={user.avatar_url} size="small" />
              <span>@{user.username}</span>
              <LogOut size={15} />
            </button>
          ) : (
            <button className="button-login" onClick={() => setAuthMode("login")}>
              Войти <ArrowRight size={15} />
            </button>
          )}
        </div>
      </header>

      <div className="app-grid">
        <aside className="left-sidebar">
          <div className="sidebar-nav">
            <button className={`nav-link ${view === "feed" ? "nav-link-active" : ""}`} onClick={() => navigate("feed")}><Home size={19} /><span>Моя лента</span><span className="nav-indicator" /></button>
            <button className={`nav-link ${view === "explore" ? "nav-link-active" : ""}`} onClick={() => navigate("explore")}><Compass size={19} /><span>Обзор</span><span className="nav-indicator" /></button>
            <button className={`nav-link ${view === "bookmarks" ? "nav-link-active" : ""}`} onClick={() => user ? navigate("bookmarks") : setAuthMode("login")}><Bookmark size={19} /><span>Закладки</span><span className="nav-indicator" /></button>
            <button className={`nav-link ${view === "profile" ? "nav-link-active" : ""}`} onClick={() => user ? navigate("profile") : setAuthMode("login")}><Users size={19} /><span>Мой профиль</span><span className="nav-indicator" /></button>
          </div>

          <div className="sidebar-rule" />
          <div className="sidebar-section">
            <div className="sidebar-section-title">
              <span>ТВОИ ТЕМЫ</span>
              <button className="icon-button-small" onClick={() => chooseCategory(undefined)} aria-label="Показать все темы"><Settings2 size={15} /></button>
            </div>
            <button className={`topic-link ${!categoryId ? "topic-link-active" : ""}`} onClick={() => chooseCategory(undefined)}>
              <span className="topic-color topic-color-all" /> Все публикации
            </button>
            {categories.map((category, index) => (
              <button
                className={`topic-link ${categoryId === category.id ? "topic-link-active" : ""}`}
                key={category.id}
                onClick={() => chooseCategory(category.id)}
              >
                <span className={`topic-color topic-color-${index % 5}`} />
                <span>{category.name}</span>
              </button>
            ))}
            {!categories.length && <span className="sidebar-empty">Темы появятся здесь</span>}
          </div>

          {user ? (
            <div className="sidebar-community-card">
              <span className="community-spark"><Sparkles size={17} /></span>
              <strong>Рады видеть,<br />@{user.username}!</strong>
              <p>Делись опытом и поддерживай других разработчиков.</p>
              <button onClick={() => setEditingPost("new")}>Написать пост <ArrowRight size={14} /></button>
            </div>
          ) : (
            <div className="sidebar-community-card">
              <span className="community-spark"><Sparkles size={17} /></span>
              <strong>Твоя история<br />начинается здесь.</strong>
              <p>Место, где идеи становятся проектами.</p>
              <button onClick={() => setAuthMode("register")}>Создать аккаунт <ArrowRight size={14} /></button>
            </div>
          )}
          <div className="sidebar-bottom">
            <span>Создано для тех, кто создаёт.</span>
            <span>© 2026 DevTalks</span>
          </div>
        </aside>

        <section key={view} className="main-column" aria-label="Публикации DevTalks">
          {view === "feed" && !appliedSearch && !categoryId && (
            <section
              className="hero-card"
              onPointerMove={moveHeroScene}
              onPointerLeave={resetHeroScene}
            >
              <div className="hero-copy">
                <span className="hero-kicker"><span className="status-dot" /> СООБЩЕСТВО РАЗРАБОТЧИКОВ</span>
                <h1>Идеи, которые<br /><span>двигают вперёд.</span></h1>
                <p>Здесь разработчики делятся тем, что создают.</p>
                <button className="hero-cta" onClick={() => user ? setEditingPost("new") : setAuthMode("register")}>
                  {user ? "Поделиться идеей" : "Стать частью сообщества"} <ArrowRight size={16} />
                </button>
              </div>
              <div className="hero-visual" aria-hidden="true">
                <div className="hero-scene">
                  <span className="hero-scene-glow" />
                  <span className="hero-grid-plane" />
                  <div className="hero-cube">
                    <span className="hero-cube-face hero-cube-front"><Code2 size={38} /></span>
                    <span className="hero-cube-face hero-cube-back">DT</span>
                    <span className="hero-cube-face hero-cube-right" />
                    <span className="hero-cube-face hero-cube-left" />
                    <span className="hero-cube-face hero-cube-top" />
                    <span className="hero-cube-face hero-cube-bottom" />
                  </div>
                  <div className="hero-float-card hero-float-card-top">
                    <span>const community =</span>
                    <strong>ideas → impact</strong>
                  </div>
                  <div className="hero-float-card hero-float-card-bottom">
                    <i /><span>BUILD IN PUBLIC</span><strong>01 / 04</strong>
                  </div>
                </div>
                <div className="hero-orbit hero-orbit-a" />
                <div className="hero-orbit hero-orbit-b" />
                <span className="hero-star hero-star-a">✳</span>
                <span className="hero-star hero-star-b">✦</span>
                <span className="hero-pixel pixel-a" /><span className="hero-pixel pixel-b" />
              </div>
            </section>
          )}

          {view === "profile" && user && (
            <section className="profile-header-card">
              <div className="profile-cover-art"><span /><i /></div>
              <div className="profile-header-main">
                <Avatar username={user.username} image={user.avatar_url} size="large" />
                <div className="profile-header-copy">
                  <span className="eyebrow">ПРОФИЛЬ РАЗРАБОТЧИКА</span>
                  <h1>@{user.username}</h1>
                  <p>{user.bio || "Добавь пару слов о себе и своих проектах."}</p>
                </div>
                <button className="button-secondary profile-edit" onClick={() => setEditingProfile(true)}>Редактировать профиль</button>
              </div>
              <div className="profile-metrics">
                <div><strong>{total}</strong><span>публикаций</span></div>
                <div><strong>{user.karma}</strong><span>karma</span></div>
                <div><strong>{new Intl.DateTimeFormat("ru-RU", { month: "long", year: "numeric" }).format(new Date(user.created_at))}</strong><span>в сообществе</span></div>
              </div>
            </section>
          )}

          {view === "explore" && (
            <section className="explore-intro">
              <span className="hero-kicker"><span className="status-dot" /> ОТКРЫВАЙ НОВОЕ</span>
              <h1>Найди свою<br /><span>следующую идею.</span></h1>
              <p>Публикации и разработчики из сообщества DevTalks.</p>
            </section>
          )}

          <div className="feed-toolbar">
            <div className="feed-title-row">
              <div>
                <h2>{currentTitle}</h2>
                <span className="feed-total">{total} {total === 1 ? "публикация" : "публикаций"}</span>
              </div>
              {view !== "bookmarks" && view !== "profile" && (
                <button className="button-refresh" onClick={refresh} aria-label="Обновить ленту"><ArrowDownWideNarrow size={16} /><span>Обновить</span></button>
              )}
            </div>

            {view === "explore" ? (
              <div className="explore-controls">
                <div className="segmented-control">
                  <button className={searchMode === "posts" ? "segment-active" : ""} onClick={() => { setSearchMode("posts"); setPage(1); }}><MessageCircle size={15} /> Публикации</button>
                  <button className={searchMode === "developers" ? "segment-active" : ""} onClick={() => { setSearchMode("developers"); setPage(1); }}><Users size={15} /> Разработчики</button>
                </div>
                {searchMode === "posts" && (
                  <div className="feed-tabs">
                    {(["new", "top", "hot"] as const).map((type) => (
                      <button key={type} className={feedType === type ? "feed-tab-active" : ""} onClick={() => { setFeedType(type); setPage(1); }}>{feedLabels[type]}</button>
                    ))}
                  </div>
                )}
              </div>
            ) : view === "feed" ? (
              <div className="feed-tabs">
                {(["new", "top", "hot"] as const).map((type) => (
                  <button key={type} className={feedType === type ? "feed-tab-active" : ""} onClick={() => { setFeedType(type); setPage(1); }}>
                    {type === "hot" ? <Flame size={15} /> : type === "top" ? <Heart size={15} /> : <Sparkles size={15} />}
                    {feedLabels[type]}
                  </button>
                ))}
              </div>
            ) : null}
          </div>

          {appliedSearch && view === "explore" && (
            <div className="search-summary">
              <Search size={15} /> Результаты для <strong>«{appliedSearch}»</strong>
              <button onClick={() => { setSearchDraft(""); setAppliedSearch(""); setPage(1); }} aria-label="Очистить поиск"><X size={15} /></button>
            </div>
          )}
          {!loading && error && (
            <div className="error-card" role="alert">
              <div><strong>Не удалось загрузить данные</strong><p>{error}</p></div>
              <button onClick={refresh}>Повторить</button>
            </div>
          )}
          {loading && (
            <div className="post-skeleton-list" aria-label="Загружаем публикации">
              {[0, 1, 2].map((item) => <div className="post-skeleton" key={item}><span /><div><i /><i /><i /></div></div>)}
            </div>
          )}

          {!loading && !error && view === "explore" && searchMode === "developers" && (
            developers.length ? (
              <div className="developer-list">{developers.map((item) => <DeveloperCard user={item} key={item.id} />)}</div>
            ) : (
              <div className="empty-card">
                <span className="empty-symbol"><Users size={23} /></span>
                <h3>Разработчиков не нашли</h3>
                <p>Попробуй изменить запрос или проверь имя пользователя.</p>
              </div>
            )
          )}

          {!loading && !error && !(view === "explore" && searchMode === "developers") && posts.length === 0 && (
            <div className="empty-card">
              <span className="empty-symbol">{view === "bookmarks" ? <Bookmark size={23} /> : <MessageCircle size={23} />}</span>
              <h3>{view === "bookmarks" ? "Здесь пока пусто" : appliedSearch ? "Ничего не нашли" : "Лента ждёт твою первую историю"}</h3>
              <p>
                {view === "bookmarks"
                  ? "Сохраняй публикации, к которым захочешь вернуться."
                  : appliedSearch
                    ? "Измени поисковый запрос или выбери другую тему."
                    : "Будь первым — поделись проектом, опытом или вопросом."}
              </p>
              {!user && view !== "bookmarks" && <button className="button-primary" onClick={() => setAuthMode("register")}>Присоединиться <ArrowRight size={15} /></button>}
              {user && view === "feed" && <button className="button-primary" onClick={() => setEditingPost("new")}><Plus size={16} /> Создать публикацию</button>}
            </div>
          )}

          {!loading && !error && posts.length > 0 && (
            <div className="post-list">
              {posts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  currentUser={user}
                  onVote={(selected) => void vote(selected)}
                  onBookmark={(selected) => void bookmark(selected)}
                  onComments={setCommentsPost}
                  onEdit={setEditingPost}
                  onDelete={(selected) => void deletePost(selected)}
                  onLogin={() => setAuthMode("login")}
                />
              ))}
            </div>
          )}

          {!loading && !error && (posts.length > 0 || developers.length > 0) && (
            <PageControls page={page} pages={pages} onChange={setPage} />
          )}
        </section>

        <aside className="right-sidebar">
          <div className="right-card identity-card">
            <div className="identity-cover"><span className="identity-glow" /><i className="identity-orbit" /></div>
            <div className="identity-content">
              <Avatar
                username={user?.username ?? "devtalks"}
                image={user?.avatar_url}
                size="large"
              />
              <span className="eyebrow">{user ? "ТВОЙ ПРОФИЛЬ" : "ТВОЁ ПРОСТРАНСТВО"}</span>
              <h3>{user ? `@${user.username}` : "Добро пожаловать!"}</h3>
              <p>{user?.bio || (user ? "Добавь описание, чтобы рассказать о себе." : "Место, где идеи становятся проектами, а проекты — историями.")}</p>
              {user ? (
                <button className="button-secondary button-wide" onClick={() => navigate("profile")}>Открыть профиль <ArrowRight size={15} /></button>
              ) : (
                <button className="button-primary button-wide" onClick={() => setAuthMode("register")}>Присоединиться <ArrowRight size={15} /></button>
              )}
            </div>
            <div className="identity-stats">
              <div><strong>{total}</strong><span>в ленте</span></div>
              <div><strong>{user?.karma ?? "—"}</strong><span>karma</span></div>
              <div><strong>{categories.length}</strong><span>темы</span></div>
            </div>
          </div>

          <div className="right-card community-card">
            <div className="right-card-heading">
              <div><span className="eyebrow">СООБЩЕСТВО</span><h3>Авторы ленты</h3></div>
              <Users size={19} />
            </div>
            {authors.length ? authors.map((author) => (
              <div className="author-row" key={author.id}>
                <Avatar username={author.username} image={author.avatar_url} size="small" />
                <div><strong>@{author.username}</strong><span>{author.karma} karma</span></div>
                <span className="author-presence" />
              </div>
            )) : <p className="right-empty">{loading ? "Загружаем авторов..." : "Авторы появятся с первыми постами."}</p>}
          </div>

          <div className="right-quote">
            <span className="quote-mark">“</span>
            <p>Лучший способ чему-то научиться — объяснить это кому-то другому.</p>
            <small>ПОДЕЛИСЬ ТЕМ, ЧТО ЗНАЕШЬ</small>
          </div>
          <div className="right-footer"><span>DevTalks · для тех, кто создаёт</span><span>© 2026</span></div>
        </aside>
      </div>

      <nav className="mobile-nav" aria-label="Основная навигация">
        <button className={view === "feed" ? "mobile-nav-active" : ""} onClick={() => navigate("feed")} aria-label="Лента"><Home size={20} /></button>
        <button className={view === "explore" ? "mobile-nav-active" : ""} onClick={() => navigate("explore")} aria-label="Обзор"><Compass size={20} /></button>
        <button className="mobile-create" onClick={() => user ? setEditingPost("new") : setAuthMode("login")} aria-label="Новая публикация"><Plus size={22} /></button>
        <button className={view === "bookmarks" ? "mobile-nav-active" : ""} onClick={() => user ? navigate("bookmarks") : setAuthMode("login")} aria-label="Закладки"><Bookmark size={20} /></button>
        <button className={view === "profile" ? "mobile-nav-active" : ""} onClick={() => user ? navigate("profile") : setAuthMode("login")} aria-label="Профиль"><Users size={20} /></button>
      </nav>

      {toast && (
        <div className="toast" role="status">
          <span className="toast-dot" /> <span>{toast}</span>
          <button onClick={() => setToast("")} aria-label="Закрыть"><X size={15} /></button>
        </div>
      )}

      {authMode && (
        <AuthDialog
          mode={authMode}
          onClose={() => setAuthMode(null)}
          onAuthed={onAuthenticated}
        />
      )}
      {editingPost && (
        <PostComposerDialog
          categories={categories}
          tags={tags}
          post={editingPost === "new" ? undefined : editingPost}
          onClose={() => setEditingPost(null)}
          onSave={savePost}
        />
      )}
      {commentsPost && (
        <CommentsDialog
          post={commentsPost}
          currentUser={user}
          onLogin={() => { setCommentsPost(null); setAuthMode("login"); }}
          onClose={() => setCommentsPost(null)}
        />
      )}
      {editingProfile && user && (
        <ProfileDialog
          user={user}
          onClose={() => setEditingProfile(false)}
          onSave={(profile) => void saveProfile(profile)}
          onAvatarUpload={uploadAvatar}
          onAvatarRemove={removeAvatar}
        />
      )}
    </main>
  );
}
