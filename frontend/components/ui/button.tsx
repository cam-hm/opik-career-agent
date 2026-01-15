import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
    "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 cursor-pointer",
    {
        variants: {
            variant: {
                default: "bg-[#424874] text-white hover:bg-[#363B5E]",
                destructive: "bg-red-500 text-white hover:bg-red-600",
                outline: "border border-gray-200 bg-white hover:bg-[#F4EEFF] text-gray-700 dark:border-gray-700/60 dark:bg-gray-800 dark:hover:bg-gray-700/50 dark:text-gray-200",
                secondary: "bg-[#DCD6F7] text-[#424874] hover:bg-[#C8C1E8]",
                ghost: "hover:bg-[#F4EEFF] dark:hover:bg-gray-700/50 text-gray-600 dark:text-gray-400",
                link: "text-[#424874] dark:text-[#A6B1E1] underline-offset-4 hover:underline",
            },
            size: {
                default: "h-10 px-4 py-2",
                sm: "h-9 rounded-md px-3",
                lg: "h-11 rounded-md px-8",
                icon: "h-10 w-10",
            },
        },
        defaultVariants: {
            variant: "default",
            size: "default",
        },
    }
)

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
    asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant, size, asChild = false, ...props }, ref) => {
        const Comp = asChild ? Slot : "button"
        return (
            <Comp
                className={cn(buttonVariants({ variant, size, className }))}
                ref={ref}
                {...props}
            />
        )
    }
)
Button.displayName = "Button"

export { Button, buttonVariants }
