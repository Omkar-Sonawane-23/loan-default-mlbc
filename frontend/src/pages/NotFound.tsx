import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div className="text-4xl font-bold text-slate-200 mb-2">404</div>
      <p className="text-sm text-slate-500 mb-4">Page not found</p>
      <Link to="/" className="btn btn-primary">Back to Dashboard</Link>
    </div>
  );
}
