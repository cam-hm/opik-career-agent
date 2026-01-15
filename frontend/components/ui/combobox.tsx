"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"

interface ComboboxProps {
    options: { label: string; value: string; group?: string }[]
    value: string
    onChange: (value: string) => void
    placeholder?: string
    searchPlaceholder?: string
    emptyText?: string
    className?: string
    allowCustom?: boolean
}

export function Combobox({
    options,
    value,
    onChange,
    placeholder = "Select option...",
    searchPlaceholder = "Search...",
    emptyText = "No option found.",
    className,
    allowCustom = false,
}: ComboboxProps) {
    const [open, setOpen] = React.useState(false)
    const [search, setSearch] = React.useState("")

    // Group options if they have a group property
    const groupedOptions = React.useMemo(() => {
        const groups: Record<string, typeof options> = {}
        const noGroup: typeof options = []

        options.forEach((opt) => {
            if (opt.group) {
                if (!groups[opt.group]) groups[opt.group] = []
                groups[opt.group].push(opt)
            } else {
                noGroup.push(opt)
            }
        })

        return { groups, noGroup }
    }, [options])

    const handleSelect = (currentValue: string) => {
        onChange(currentValue === value ? "" : currentValue)
        setOpen(false)
    }

    const handleCustom = () => {
        if (allowCustom && search) {
            onChange(search)
            setOpen(false)
        }
    }

    const selectedLabel = options.find((framework) => framework.value === value)?.label || value

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    className={cn("w-full justify-between h-11 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700/60 font-normal", className)}
                >
                    {value ? selectedLabel : <span className="text-muted-foreground">{placeholder}</span>}
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-[--radix-popover-trigger-width] p-0" align="start">
                <Command>
                    <CommandInput placeholder={searchPlaceholder} onValueChange={setSearch} />
                    <CommandList>
                        <CommandEmpty>
                            {allowCustom ? (
                                <button
                                    className="w-full text-left py-2 px-4 text-sm text-muted-foreground cursor-pointer hover:bg-accent hover:text-accent-foreground"
                                    onClick={handleCustom}
                                    type="button"
                                >
                                    Use "{search}"
                                </button>
                            ) : (
                                emptyText
                            )}
                        </CommandEmpty>

                        {/* Render grouped options */}
                        {Object.entries(groupedOptions.groups).map(([groupName, groupOpts]) => (
                            <CommandGroup key={groupName} heading={groupName}>
                                {groupOpts.map((framework) => (
                                    <CommandItem
                                        key={framework.value}
                                        value={framework.value}
                                        onSelect={() => handleSelect(framework.value)}
                                    >
                                        <Check
                                            className={cn(
                                                "mr-2 h-4 w-4",
                                                value === framework.value ? "opacity-100" : "opacity-0"
                                            )}
                                        />
                                        {framework.label}
                                    </CommandItem>
                                ))}
                            </CommandGroup>
                        ))}

                        {/* Render ungrouped options */}
                        {groupedOptions.noGroup.length > 0 && (
                            <CommandGroup>
                                {groupedOptions.noGroup.map((framework) => (
                                    <CommandItem
                                        key={framework.value}
                                        value={framework.value}
                                        onSelect={() => handleSelect(framework.value)}
                                    >
                                        <Check
                                            className={cn(
                                                "mr-2 h-4 w-4",
                                                value === framework.value ? "opacity-100" : "opacity-0"
                                            )}
                                        />
                                        {framework.label}
                                    </CommandItem>
                                ))}
                            </CommandGroup>
                        )}

                    </CommandList>
                </Command>
            </PopoverContent>
        </Popover>
    )
}
