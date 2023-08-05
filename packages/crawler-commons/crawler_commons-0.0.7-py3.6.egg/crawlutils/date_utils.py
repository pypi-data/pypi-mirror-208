
####
### %Y : yyyy
### %m : mm
### %d : dd
def date_format(dt, pattern="%Y%m%d"):
    return dt.strftime(pattern)


def get_quarter_start_date(quarter):
    month = int(quarter) % 100
    month -= 2

    return f"{month:02d}.01"


def get_last_quarter(year_month, step=1):
    year_month = int(year_month)
    year_month -= 1
    quarters = [3, 6, 9, 12]
    while year_month % 100 not in quarters:
        year_month -= 1
        if year_month % 100 == 0:
            year_month -= 100
            year_month += 12
    if step == 1:
        return year_month
    else:
        return get_last_quarter(year_month, step=step-1)


def time_in_range(start, end, dt):
    fmt = "%Y-%m-%d_%H:%M"
    if start <= end:
        return start <= dt <= end
    else:
        print(f"dt [{dt.strftime(fmt)}] is not in range(start : [{start.strftime(fmt)}], end : [{end.strftime(fmt)}]")
        return start <= dt or dt <= end


if __name__ == "__main__":
    print(f"get_last_quarter(202207) : {get_last_quarter('202207')}")
    print(f"get_last_quarter(202206) : {get_last_quarter(202206)}")
    print(f"get_last_quarter(202205) : {get_last_quarter(202205)}")