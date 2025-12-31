# Example - Craft Drift Nets in Runescape

!!! warning 
    This is just an example to showcase language features, it will likely result in a ban if actually used as this is considered cheating

## Prerequisites
- Bank pin entered
- start in front of fossil island bank, inventory full of jute
- zoom out enough to see loom and bank at the same time
- take screenshots to support the @find_template calls (good to use runelite plugin to highlight loom/bank two colors like blue/red to make them more findable, but images of the raw objects may work too)

```
@set_template_dir("<YOUR DIRECTORY>");

# random value between 1500, 2200
fn fast_pps() {
    return @rand(1500,2200);
}

fn short_wait() {
    @wait(50, 62);  # Random wait 50-62ms
}

fn count_jute_in_inv() {
    item_count = @find_templates("jute_bundle", 28);
    if item_count == null {
        return 0;
    }

    return @len(item_count);
}

fn withdraw_jute_from_bank() {
    jute_x, jute_y = @find_template("unbank_jute");
    if jute_x != null {
        @mouse_move(jute_x, jute_y, fast_pps(), 1);
        short_wait();
        @left_click();
        return true;
    }
    return false;
}

fn click_jute() {
    jute_x, jute_y = @find_template("jute_bundle");
    if jute_x != null {
        @mouse_move(jute_x, jute_y, fast_pps(), 1);
        short_wait();
        @left_click();
        return true;
    }
    return false;
}

fn move_mouse_to_chest() {
    chest_x, chest_y = @find_template("jute_chest");
    if chest_x != null {
        @mouse_move(chest_x, chest_y, fast_pps(), 1);
        return true;
    }
    return false;
}

fn click_chest() {
    moved = move_mouse_to_chest();
    if moved == false {
        return false;
    }
    short_wait();
    @left_click();
    return true;
}

fn click_loom() {
    loom_x, loom_y = @find_template("jute_loom");
    if loom_x != null {
        @mouse_move(loom_x, loom_y, fast_pps(), 1);
        short_wait();
        @left_click();
        return true;
    }
    return false;
}

fn wait_for_loom() {
    # poll until loom is found
    total_wait = 0;
    while true {
        # jute_arrive is a screenshot of the prompt that asks you what to craft
        loom_x, loom_y = @find_template("jute_arrive");
        if loom_x != null {
            return true;
        }
        @wait(200);
        total_wait = total_wait + 200;
        if total_wait > 20000 {
            @print("waiting for loom timed out, retrying click");
            return false;
        }
    }
}

nets = null;
fn wait_for_bank() {
    # outer to specify scope
    outer nets;
    # poll until bank is found
    if nets != null {
        # pre-move mouse to net, shuffle to avoid hovering over same net every time
        nets = @shuffle(nets);
        net_x, net_y = nets[0];
        @mouse_move(net_x, net_y, fast_pps(), true);
    }

    while true {
        bank_x, bank_y = @find_template("bank_open");
        if bank_x != null {
            return null;
        }
        short_wait();
    }
}

fn close_bank() {
    bank_close_x, bank_close_y = @find_template("close_bank");
    if bank_close_x != null {
        @mouse_move(bank_close_x, bank_close_y, fast_pps(), 1);
        short_wait();
        @left_click();
    }
}

fn bank() {
    # get some from chest
    clicked = click_chest();
    if clicked == false {
        @print("Jute chest not found");
    }

    @print("walking to bank");
    wait_for_bank();
    # bank the net by clicking it
    outer nets;
    if nets == null {
        nets = @find_templates("net", 10);
        net_x, net_y = nets[0];
        if net_x != null {
            @mouse_move(net_x, net_y, fast_pps(), 1);
            short_wait();
            @left_click();
        } else {
            @print("net not found in bank");
        }
    }
    if nets != null {
        @left_click(); # should have pre-moved to net
    }

    # bank it
    @print("withdraw jute in bank");
    withdraw_jute_from_bank();
    short_wait();
    @print("closing bank");
    close_bank();
}

fn run() {
    while true {
        jute_count = count_jute_in_inv();
        @print("Jute bundles in inv: " + jute_count);
        if jute_count < 2 {
            # means full of drift nets, bank them
            @print("no jute, banking");
            bank();
        } else {
            # make some nets!
            @print("move to loom");
            click_loom();
            if wait_for_loom() == false {
                # timed out, just retry whole loop (go back to banking)
                bank();
                continue;
            }
            @print("arrived at loom, crafting");
            # send space to craft
            short_wait();
            @press_and_release(50, "space");

            @print("waiting for jute to be used up");
            rem = count_jute_in_inv();
            rand_move_mouse = @rand_i(1, 10) * 2;
            @print("will move mouse to bank when " + rand_move_mouse + " jute bundles remain");

            # while there is still jute to craft
            while rem > 1 {
                # randomly pre-move cursor to bank
                if rem == rand_move_mouse {
                    @print("pre move mouse to bank");
                    bank_x, bank_y = @find_template("jute_chest");
                    if bank_x != null {
                        # move mouse to left a bit to not block chest
                        mouse_pos_x, mouse_pos_y = @mouse_position();
                        @mouse_move(bank_x - @rand(75, 100), bank_y - @rand(75, 100), fast_pps()/2, 1);
                    }
                    
                }
                @print("Jute bundles remaining: " + rem);
                short_wait();
                rem = count_jute_in_inv();
            }
        }
        short_wait();
    }
}

@print("running jute.macroni");
run();
```