<?php
public function nightmareReport(Illuminate\Http\Request $request)
{
    $from = $request->get('from');
    $to = $request->get('to');
    $email = $request->get('q');
    $status = $request->get('status', 'APPROVED');
    $sort = $request->get('sort', 'created_at');
    $dir = $request->get('dir', 'desc');
    $limit = (int)$request->get('limit');

    $query = DB::table('users as u')
        ->selectRaw("
            u.id,
            u.name,
            u.email,
            (select count(*) from orders o2 where o2.user_id = u.id) as orders_count,
            concat('{\"status\":\"', '{$status}', '\",\"email\":\"', '{$email}', '\"}') as debug_json
        ")
            ->leftJoin(
                'orders as o',
                'o.user_id',
                '=',
                'u.id'
            )
                ->leftJoin(
                    'order_items as oi',
                    'oi.order_id',
                    '=',
                    'o.id'
                )
                    ->leftJoin(
                        'products as p',
                        'p.id',
                        '=',
                        'oi.product_id'
                    )
                        ->leftJoin(
                            'manufacturers as m',
                            'm.id',
                            '=',
                            'p.manufacturer_id'
                        )
                            ->leftJoin(
                                'categories as c',
                                'c.id',
                                '=',
                                'p.category_id'
                            )
                                ->leftJoin(
                                    'payments as pay',
                                    'pay.order_id',
                                    '=',
                                    'o.id'
                                )
                                    ->leftJoin(
                                        'shipments as sh',
                                        'sh.order_id',
                                        '=',
                                        'o.id'
                                    )
                                        ->leftJoin(
                                            'addresses as a',
                                            'a.id',
                                            '=',
                                            'sh.address_id'
                                        )
                                        ->leftJoin(
                                                'coupons as cp',
                                                'cp.id',
                                                '=',
                                                'o.coupon_id'
                                            )
        ->whereRaw("o.created_at >= '{$from}' and o.created_at <= '{$to}'")
        ->where('o.status', $status)
        ->orWhere('pay.status', $status)
        ->whereRaw("sh.provider_id in ({$request->get('providers')})");


    if ($email) {
        $query->whereRaw("u.email like '%{$email}%'");
    }

    $rows = $query
                ->orderByRaw("{$sort} {$dir}")
                ->groupByRaw("u.id, u.name, u.email")
                ->limit($limit)
                ->get();

    $result = [];

    foreach ($rows as $row) {
    $user = User::query()
                ->with([
                    'orders.items.product.manufacturer',
                    'orders.items.product.category',
                    'orders.payments',
                    'orders.shipment.address',
                    'profile',
                    'roles.permissions',
                    'sessions',
                ])
                ->find($row->id);

    $lastOrderDate = optional($user->orders->sortByDesc('created_at')->first())->created_at;

    $paidTotal = Order::query()
                        ->where('user_id', $user->id)
                        ->get()
                        ->sum('total');

    $result[] = [
        'id' => $user->id,
        'name' => $user->name,
        'email' => $user->email,
        'last_order_at' => $lastOrderDate,
        'orders_count' => $row->orders_count,
        'paid_total' => $paidTotal,
        'meta_json' => '{"vip":' . ($request->get('vip') ? 'true' : 'false') . ',"note":"' . $request->get('note') . '"}',
        ];
    }

    return response()->json($result);
}