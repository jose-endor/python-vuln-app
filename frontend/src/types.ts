export type Book = {
  id: number;
  title: string;
  author: string;
  isbn: string;
  cover: string;
  category: string;
  summary: string;
};

export type Me = { id: number; username: string; role: string } | null;
