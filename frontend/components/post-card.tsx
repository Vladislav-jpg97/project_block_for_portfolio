"use client";

import { useState } from "react";
import {
  Bookmark,
  Check,
  Eye,
  Heart,
  MessageCircle,
  MoreHorizontal,
  Pencil,
  Send,
  Trash2,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Post, User } from "@/types/api";

export function Avatar({
  username,
  image,
  size = "medium",
}: {
  username: string;
  image?: string | null;
  size?: "small" | "medium" | "large";
}) {
  return (
    <span
      className={`avatar avatar-${size}`}
      style={image ? { backgroundImage: `url("${image}")` } : undefined}
      aria-label={`Аватар ${username}`}
    >
      {!image && username.slice(0, 1).toUpperCase()}
    </span>
  );
}

function formatDate(value: string) {
  const date = new Date(value);
  const elapsed = Date.now() - date.getTime();
  if (elapsed < 60_000) return "только что";
  if (elapsed < 60 * 60_000) return `${Math.floor(elapsed / 60_000)} мин назад`;
  if (elapsed < 24 * 60 * 60_000) return `${Math.floor(elapsed / (60 * 60_000))} ч назад`;
  return new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "short",
  }).format(date);
}

export function PostCard({
  post,
  currentUser,
  onVote,
  onBookmark,
  onComments,
  onEdit,
  onDelete,
  onLogin,
}: {
  post: Post;
  currentUser: User | null;
  onVote: (post: Post) => void;
  onBookmark: (post: Post) => void;
  onComments: (post: Post) => void;
  onEdit: (post: Post) => void;
  onDelete: (post: Post) => void;
  onLogin: () => void;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const isOwner = currentUser?.id === post.author.id;

  async function sharePost() {
    const url = `${window.location.origin}/?post=${encodeURIComponent(post.slug)}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      window.open(url, "_blank", "noopener,noreferrer");
    }
  }

  return (
    <article className="post-card">
      <div className="post-header">
        <Avatar username={post.author.username} image={post.author.avatar_url} />
        <div className="post-author">
          <strong>@{post.author.username}</strong>
          <span>
            {formatDate(post.created_at)}
            {post.category && <><i className="meta-dot" />{post.category.name}</>}
          </span>
        </div>
        <div className="post-menu-wrap">
          <button
            className="icon-button post-menu-trigger"
            aria-label="Действия с публикацией"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
          >
            <MoreHorizontal size={19} />
          </button>
          {menuOpen && (
            <div className="post-menu">
              {isOwner ? (
                <>
                  <button onClick={() => { setMenuOpen(false); onEdit(post); }}><Pencil size={15} /> Редактировать</button>
                  <button className="menu-danger" onClick={() => { setMenuOpen(false); onDelete(post); }}><Trash2 size={15} /> Удалить</button>
                </>
              ) : (
                <span>Публикация DevTalks</span>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="post-main">
        <h3>{post.title}</h3>
        <div className="post-markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{post.content}</ReactMarkdown>
        </div>
      </div>

      {post.tags.length > 0 && (
        <div className="post-tags">
          {post.tags.map((tag) => <span key={tag.id}>#{tag.name}</span>)}
        </div>
      )}

      <div className="post-footer">
        <div className="post-actions">
          <button
            className={`post-action ${post.user_vote ? "post-action-liked" : ""}`}
            onClick={() => currentUser ? onVote(post) : onLogin()}
            aria-label={post.user_vote ? "Убрать голос" : "Голосовать"}
            title={currentUser ? undefined : "Войди, чтобы проголосовать"}
          >
            <Heart size={18} fill={post.user_vote ? "currentColor" : "none"} />
            <span>{post.votes_count}</span>
          </button>
          <button className="post-action" onClick={() => onComments(post)} aria-label="Комментарии">
            <MessageCircle size={18} />
            <span>Обсудить</span>
          </button>
          <span className="post-views"><Eye size={15} /> {post.views_count}</span>
        </div>
        <div className="post-actions post-actions-end">
          <button
            className={`icon-button post-action-icon ${post.is_bookmarked ? "post-action-saved" : ""}`}
            onClick={() => currentUser ? onBookmark(post) : onLogin()}
            aria-label={post.is_bookmarked ? "Убрать из закладок" : "Сохранить"}
            title={currentUser ? undefined : "Войди, чтобы сохранить"}
          >
            <Bookmark size={18} fill={post.is_bookmarked ? "currentColor" : "none"} />
          </button>
          <button className="icon-button post-action-icon" onClick={() => void sharePost()} aria-label="Поделиться ссылкой">
            {copied ? <Check size={17} /> : <Send size={17} />}
          </button>
        </div>
      </div>
    </article>
  );
}
