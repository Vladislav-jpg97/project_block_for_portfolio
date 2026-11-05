"use client";

import { FormEvent, ReactNode, useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  Check,
  ImagePlus,
  LoaderCircle,
  MessageCircle,
  Reply,
  Send,
  Trash2,
  X,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api, saveSession } from "@/lib/api";
import type { Category, Comment, Post, PostInput, Tag, User } from "@/types/api";
import { Avatar } from "@/components/post-card";

type DialogShellProps = {
  eyebrow: string;
  title: string;
  description?: string;
  onClose: () => void;
  children: ReactNode;
  wide?: boolean;
};

function DialogShell({
  eyebrow,
  title,
  description,
  onClose,
  children,
  wide,
}: DialogShellProps) {
  return (
    <div
      className="dialog-backdrop"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        className={`dialog-panel ${wide ? "dialog-panel-wide" : ""}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
      >
        <button className="dialog-x" onClick={onClose} aria-label="Закрыть">
          <X size={19} />
        </button>
        <span className="eyebrow">{eyebrow}</span>
        <h2 id="dialog-title">{title}</h2>
        {description && <p className="dialog-description">{description}</p>}
        {children}
      </section>
    </div>
  );
}

export function AuthDialog({
  mode: initialMode,
  onClose,
  onAuthed,
}: {
  mode: "login" | "register";
  onClose: () => void;
  onAuthed: (user: User) => void;
}) {
  const [mode, setMode] = useState(initialMode);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const username = String(form.get("username") ?? "");
    const password = String(form.get("password") ?? "");
    try {
      if (mode === "register") {
        await api.register(
          username,
          String(form.get("email") ?? ""),
          password,
        );
      }
      const tokens = await api.login(username, password);
      saveSession(tokens);
      onAuthed(await api.me());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Не удалось выполнить вход.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <DialogShell
      eyebrow={mode === "register" ? "СОЗДАЙ СВОЙ ПРОФИЛЬ" : "СНОВА РАДЫ ТЕБЯ ВИДЕТЬ"}
      title={mode === "register" ? "Присоединяйся к нам." : "Войти в DevTalks."}
      description={
        mode === "register"
          ? "Делись идеями, находи единомышленников и вдохновляй."
          : "Твоя лента и сообщество уже заждались."
      }
      onClose={onClose}
    >
      <form className="dialog-form" onSubmit={submit}>
        <label>
          Имя пользователя
          <input
            name="username"
            autoComplete="username"
            placeholder="например, alex_dev"
            minLength={3}
            maxLength={100}
            pattern="[a-zA-Z0-9_-]+"
            required
          />
        </label>
        {mode === "register" && (
          <label>
            Электронная почта
            <input
              type="email"
              name="email"
              autoComplete="email"
              placeholder="you@example.com"
              required
            />
          </label>
        )}
        <label>
          Пароль
          <input
            type="password"
            name="password"
            autoComplete={mode === "register" ? "new-password" : "current-password"}
            placeholder="Не менее 8 символов"
            minLength={8}
            required
          />
          {mode === "register" && (
            <span className="field-note">
              Добавь заглавную и строчную букву, а также цифру.
            </span>
          )}
        </label>
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="button-primary button-wide" disabled={busy}>
          {busy ? (
            <><LoaderCircle className="spin" size={17} /> Подождите...</>
          ) : (
            <>{mode === "register" ? "Создать аккаунт" : "Войти"} <ArrowRight size={17} /></>
          )}
        </button>
      </form>
      <p className="switch-auth">
        {mode === "register" ? "Уже есть аккаунт?" : "Впервые здесь?"}{" "}
        <button
          className="text-button"
          onClick={() => {
            setError("");
            setMode(mode === "register" ? "login" : "register");
          }}
        >
          {mode === "register" ? "Войти" : "Создать аккаунт"}
        </button>
      </p>
    </DialogShell>
  );
}

export function PostComposerDialog({
  categories,
  tags,
  post,
  onClose,
  onSave,
}: {
  categories: Category[];
  tags: Tag[];
  post?: Post;
  onClose: () => void;
  onSave: (body: PostInput) => Promise<void>;
}) {
  const [title, setTitle] = useState(post?.title ?? "");
  const [content, setContent] = useState(post?.content ?? "");
  const [categoryId, setCategoryId] = useState(
    post?.category?.id ? String(post.category.id) : "",
  );
  const [selectedTags, setSelectedTags] = useState<number[]>(
    post?.tags.map((tag) => tag.id) ?? [],
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function toggleTag(id: number) {
    setSelectedTags((current) =>
      current.includes(id)
        ? current.filter((tagId) => tagId !== id)
        : current.length < 5
          ? [...current, id]
          : current,
    );
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await onSave({
        title,
        content,
        category_id: Number(categoryId),
        tags_ids: selectedTags,
        is_published: post?.is_published ?? true,
      });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Не удалось сохранить пост.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <DialogShell
      eyebrow="ТВОЯ ИДЕЯ — ВАЖНА"
      title={post ? "Редактировать публикацию" : "Новая публикация"}
      description="Расскажи о проекте, опыте или вопросе — сообщество подключится."
      onClose={onClose}
      wide
    >
      <form className="dialog-form" onSubmit={submit}>
        <label>
          Заголовок
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="О чём ты хочешь рассказать?"
            minLength={5}
            maxLength={200}
            required
          />
        </label>
        <label>
          Тема
          <select
            value={categoryId}
            onChange={(event) => setCategoryId(event.target.value)}
            required
          >
            <option value="" disabled>Выбери тему публикации</option>
            {categories.map((category) => (
              <option value={category.id} key={category.id}>{category.name}</option>
            ))}
          </select>
          {categories.length === 0 && (
            <span className="field-note">Пока нет доступных тем для публикации.</span>
          )}
        </label>
        <label>
          Твоя история
          <textarea
            value={content}
            onChange={(event) => setContent(event.target.value)}
            placeholder="Поделись опытом, расскажи о проекте или задай вопрос..."
            minLength={1}
            rows={7}
            required
          />
          <span className="field-note">
            {content.trim().length} символов · Пустую публикацию отправить нельзя · Markdown поддерживается
          </span>
        </label>
        {tags.length > 0 && (
          <fieldset className="tag-picker">
            <legend>Теги <span>до 5</span></legend>
            <div className="tag-picker-list">
              {tags.map((tag) => (
                <button
                  type="button"
                  className={`tag-choice ${selectedTags.includes(tag.id) ? "tag-choice-active" : ""}`}
                  key={tag.id}
                  onClick={() => toggleTag(tag.id)}
                  aria-pressed={selectedTags.includes(tag.id)}
                >
                  {selectedTags.includes(tag.id) && <Check size={13} />}
                  {tag.name}
                </button>
              ))}
            </div>
          </fieldset>
        )}
        {error && <p className="form-error" role="alert">{error}</p>}
        <button
          className="button-primary button-wide"
          disabled={busy || categories.length === 0}
        >
          {busy ? <><LoaderCircle className="spin" size={17} /> Сохраняем...</> : <><Send size={16} /> {post ? "Сохранить изменения" : "Опубликовать"}</>}
        </button>
      </form>
    </DialogShell>
  );
}

function CommentItem({
  comment,
  depth,
  onReply,
  currentUser,
  deletingCommentId,
  onDelete,
}: {
  comment: Comment;
  depth: number;
  onReply: (comment: Comment) => void;
  currentUser: User | null;
  deletingCommentId: number | null;
  onDelete: (comment: Comment) => void;
}) {
  const deleting = deletingCommentId === comment.id;
  return (
    <div className={`comment-thread ${depth > 0 ? "comment-thread-nested" : ""}`}>
      <div className="comment-avatar">{comment.author.username.slice(0, 1).toUpperCase()}</div>
      <div className="comment-body">
        <div className="comment-author-line">
          <strong>@{comment.author.username}</strong>
          <time>{new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "short" }).format(new Date(comment.created_at))}</time>
          {currentUser?.id === comment.author.id && (
            <button
              className="comment-delete"
              onClick={() => onDelete(comment)}
              disabled={deleting}
              aria-label="Удалить свой комментарий"
              title="Удалить комментарий"
            >
              {deleting ? <LoaderCircle className="spin" size={14} /> : <Trash2 size={14} />}
            </button>
          )}
        </div>
        <p>{comment.content}</p>
        <button className="reply-button" onClick={() => onReply(comment)}>
          <Reply size={13} /> Ответить
        </button>
        {comment.replies.map((reply) => (
          <CommentItem
            key={reply.id}
            comment={reply}
            depth={depth + 1}
            onReply={onReply}
            currentUser={currentUser}
            deletingCommentId={deletingCommentId}
            onDelete={onDelete}
          />
        ))}
      </div>
    </div>
  );
}

export function CommentsDialog({
  post,
  currentUser,
  onLogin,
  onClose,
}: {
  post: Post;
  currentUser: User | null;
  onLogin: () => void;
  onClose: () => void;
}) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [text, setText] = useState("");
  const [parent, setParent] = useState<Comment | null>(null);
  const [loadedPostId, setLoadedPostId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [deletingCommentId, setDeletingCommentId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const loading = loadedPostId !== post.id;
  const canComment = currentUser !== null;

  const loadComments = async () => {
    setError("");
    try {
      setComments(await api.comments(post.id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Не удалось загрузить комментарии.");
    }
  };

  useEffect(() => {
    let active = true;
    void api.comments(post.id)
      .then((result) => {
        if (active) {
          setComments(result);
          setError("");
        }
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof Error ? reason.message : "Не удалось загрузить комментарии.");
        }
      })
      .finally(() => {
        if (active) setLoadedPostId(post.id);
      });
    return () => {
      active = false;
    };
  }, [post.id]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!text.trim()) return;
    setBusy(true);
    setError("");
    try {
      await api.createComment(post.id, text.trim(), parent?.id ?? null);
      setText("");
      setParent(null);
      await loadComments();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Не удалось отправить комментарий.");
    } finally {
      setBusy(false);
    }
  }

  async function deleteComment(comment: Comment) {
    if (!window.confirm("Удалить свой комментарий?")) return;
    setDeletingCommentId(comment.id);
    setError("");
    try {
      await api.deleteComment(post.id, comment.id);
      if (parent?.id === comment.id) setParent(null);
      setComments(await api.comments(post.id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Не удалось удалить комментарий.");
    } finally {
      setDeletingCommentId(null);
    }
  }

  return (
    <DialogShell
      eyebrow="ОБСУЖДЕНИЕ"
      title={post.title}
      description={`Публикация @${post.author.username}`}
      onClose={onClose}
      wide
    >
      <article className="discussion-post">
        <span className="eyebrow">ИСТОРИЯ</span>
        <div className="post-markdown discussion-post-content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{post.content}</ReactMarkdown>
        </div>
        {post.tags.length > 0 && (
          <div className="post-tags">
            {post.tags.map((tag) => <span key={tag.id}>#{tag.name}</span>)}
          </div>
        )}
      </article>
      <div className="comments-list">
        {loading && <div className="inline-loading"><LoaderCircle className="spin" size={18} /> Загружаем комментарии...</div>}
        {!loading && comments.length === 0 && !error && (
          <div className="comments-empty">
            <MessageCircle size={23} />
            <p>Пока тихо. Начни разговор первым.</p>
          </div>
        )}
        {error && <p className="form-error" role="alert">{error}</p>}
        {!loading && comments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            depth={0}
            onReply={setParent}
            currentUser={currentUser}
            deletingCommentId={deletingCommentId}
            onDelete={(selected) => void deleteComment(selected)}
          />
        ))}
      </div>
      {canComment ? (
        <form className="comment-compose" onSubmit={submit}>
          {parent && (
            <div className="replying-to">
              Ответ для @{parent.author.username}
              <button type="button" onClick={() => setParent(null)} aria-label="Отменить ответ"><X size={14} /></button>
            </div>
          )}
          <textarea
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Напиши комментарий..."
            maxLength={512}
            rows={3}
            required
          />
          <button className="button-primary" disabled={busy || !text.trim()}>
            {busy ? <LoaderCircle className="spin" size={16} /> : <Send size={15} />}
            Отправить
          </button>
        </form>
      ) : (
        <button className="button-secondary button-wide" onClick={onLogin}>
          Войди, чтобы участвовать в обсуждении <ArrowRight size={16} />
        </button>
      )}
    </DialogShell>
  );
}

export function ProfileDialog({
  user,
  onClose,
  onSave,
  onAvatarUpload,
  onAvatarRemove,
}: {
  user: User;
  onClose: () => void;
  onSave: (user: User) => void;
  onAvatarUpload: (file: File) => Promise<User>;
  onAvatarRemove: () => Promise<User>;
}) {
  const [username, setUsername] = useState(user.username);
  const [email, setEmail] = useState(user.email);
  const [bio, setBio] = useState(user.bio ?? "");
  const [busy, setBusy] = useState(false);
  const [avatarBusy, setAvatarBusy] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState(user.avatar_url);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function selectAvatar(file?: File) {
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      setError("Максимальный размер аватара — 5 МБ.");
      return;
    }
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Выбери изображение JPEG, PNG или WebP.");
      return;
    }
    setAvatarBusy(true);
    setError("");
    try {
      const profile = await onAvatarUpload(file);
      setAvatarUrl(profile.avatar_url);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Не удалось загрузить аватар.");
    } finally {
      setAvatarBusy(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function removeAvatar() {
    setAvatarBusy(true);
    setError("");
    try {
      const profile = await onAvatarRemove();
      setAvatarUrl(profile.avatar_url);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Не удалось удалить аватар.");
    } finally {
      setAvatarBusy(false);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      onSave(await api.updateProfile({ username, email, bio: bio.trim() || null }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Не удалось обновить профиль.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <DialogShell
      eyebrow="ТВОЙ ПРОФЕССИОНАЛЬНЫЙ ПРОФИЛЬ"
      title="Обновить профиль"
      description="Покажи сообществу, кто ты и чем занимаешься."
      onClose={onClose}
    >
      <form className="dialog-form" onSubmit={submit}>
        <div className="avatar-editor">
          <Avatar username={username} image={avatarUrl} size="large" />
          <div className="avatar-editor-actions">
            <strong>Фото профиля</strong>
            <span>JPEG, PNG или WebP · до 5 МБ</span>
            <div>
              <button
                type="button"
                className="button-secondary"
                onClick={() => fileInputRef.current?.click()}
                disabled={avatarBusy}
              >
                {avatarBusy ? <LoaderCircle className="spin" size={15} /> : <ImagePlus size={15} />}
                {avatarBusy ? "Обновляем..." : avatarUrl ? "Заменить фото" : "Добавить фото"}
              </button>
              {avatarUrl && (
                <button
                  type="button"
                  className="button-secondary avatar-remove-button"
                  onClick={() => void removeAvatar()}
                  disabled={avatarBusy}
                >
                  <Trash2 size={15} /> Удалить
                </button>
              )}
              <input
                ref={fileInputRef}
                className="visually-hidden"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={(event) => void selectAvatar(event.target.files?.[0])}
              />
            </div>
          </div>
        </div>
        <label>
          Имя пользователя
          <input value={username} onChange={(event) => setUsername(event.target.value)} minLength={3} maxLength={100} pattern="[a-zA-Z0-9_-]+" required />
        </label>
        <label>
          Электронная почта
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <label>
          О себе
          <textarea value={bio} onChange={(event) => setBio(event.target.value)} maxLength={512} rows={4} placeholder="Расскажи о своём опыте, интересах и проектах..." />
          <span className="field-note">{bio.length}/512 символов</span>
        </label>
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="button-primary button-wide" disabled={busy}>
          {busy ? <><LoaderCircle className="spin" size={17} /> Сохраняем...</> : <>Сохранить профиль <ArrowRight size={16} /></>}
        </button>
      </form>
    </DialogShell>
  );
}
