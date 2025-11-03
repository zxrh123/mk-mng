import { cva, type VariantProps } from "class-variance-authority";
import { ButtonHTMLAttributes, forwardRef } from "react";

import { cn } from "../../lib/utils";

const buttonVariants = cva(
  "relative inline-flex items-center justify-center rounded-full px-6 py-2.5 font-semibold uppercase tracking-widest transition duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-midnight",
  {
    variants: {
      variant: {
        primary: "bg-neon text-midnight shadow-glow hover:shadow-neon",
        secondary: "bg-glass text-white border border-azure/40 backdrop-blur-md hover:border-neon",
        ghost: "bg-transparent text-neon hover:text-white"
      }
    },
    defaultVariants: {
      variant: "primary"
    }
  }
);

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, ...props }, ref) => (
  <button ref={ref} className={cn(buttonVariants({ variant, className }))} {...props} />
));

Button.displayName = "Button";

export { Button, buttonVariants };
