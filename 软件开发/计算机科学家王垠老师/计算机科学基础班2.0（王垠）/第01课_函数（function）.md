[TOC]

# 课堂笔记

## 变量、表达式、计算图
![[20210323210454768_3013.png]]

计算图中没有括号，却能表示先后顺序，类似电路。
```js
//制造一个变量,名字叫x,等号的右边是一个表达式,表达式的结果,会被作为该变量的值。
var x = 2 * 3;
//step1:先计算2 * 3的结果，得到6。
//step2:机器内部产生一个变量x，该变量像指针一样，并指向6这个结果。
//step3:其中2 * 3是个表达式,算出6这个值,这整个表达式到计算出6这个结果,该过程叫求职。
```

## 函数
```js
//定义函数
x => x * x;//输出:x => x * x    (这里的x表示变量)
(x => x * x);//输出:x => x * x

//调用
(x => x * x)(3);//输出:9
//调用:给函数一个输入的操作叫调用。
//输入:=>的左边叫输入。
//输出:=>的右边叫函数体，也叫输出。

//给函数起名字
var square = x => x * x;
square;//输出:x => x * x  (表示func就指向一个函数,输入部分是x,函数体是x * x)
square(3);//输出:9
1 + square(3);//输出:10
//函数跟数字是同等地位的，所以出现数字的地方，都可以用变量或者函数替代

//单步替换
(x => x * x)(3)//把x替换成了x的值,即替换成3,这是一个思维的模型。
(x => 2 * (x + 3))(5)//单步替换结果:2 * (5 + 3)
(x, y) => x + 2 * y //输出:(x, y) => x + 2 * y
(x, y) => x + 2 * y(1, 3)//输出:7

x => (y => x + y)//输入是x,输出是 y => x + y
(x => (y => x + y))(2)//输出:y => x + y
(x => (y => x + y))(2)(3)//输出:5

var f = x => (y => x + y);//输出:x => (y => x + y)
var f = (x => (y => x + y))(2);//输出:y => x + y

//函数参数只能在函数体里面看见，无论如何，函数外面无法对应相同变量名都不会被函数体内改变。
//类似于C语言里的函数普通形参，就是那种非指针的整型形参。

var apply = (f, x) => f(x);
//调用有两部分：操作数、操作符，f为操作符，x为操作数。

apply(x => x * x, 3)//输出:9
```

![[20210323210555448_12734.png]]

```js
apply(square, x)//输出:36
```

```js
var compose = (f, g) => x => f(g(x));//输入是(f, g), 且f和g都是函数
compose//输出:(f, g) => x => f(g(x))
compose(x => x * x, x => x + 1)//输出:x => f(g(x))
var h1 = compose(x => x * x, x => x + 1)
h1//输出:x => f(g(x))
h1(3)//输出:16
//不用写compose就把右边函数体表达出来:
var h1 = x => (x + 1) * (x + 1)
h1//输出:x => (x + 1) * (x + 1)
(x => (x + 1) * (x + 1))(3) //输出:16
```

compose组合函数原理示意图:
![[20210323210631368_31656.png]]

使用function来定义函数，这样易读（比var容易判断这是个函数）:
```js
function f(x)
{
    return x * x;
}
f//输出:整个大括号函数体，包括大括号
f(3)//输出:9

function f(x)
{
    return x => x * x;
}
f(3)//输出:x => x * x
```

# 作业提交与反馈(微信多对一辅导群)
多对一辅导群：每一位学生都有自己独立的辅导群，这个辅导群里有多位老师，方便学生提问不会被其他学生淹没。
![[20210323210715033_4253.png]]

![[20210323210739496_18192.png]]


## area
原题：写一个函数，名字叫 area。它的参数是 r（圆的半径），输出是圆的面积（你可以自己查一下面积公式）。因为圆周率 pi 是一个“常数”（永远不变的数），可以先定义一个变量 pi，然后在 area 函数里使用它。
提示：为了美观，请注意在算术操作符两边加上空格，比如 2 * 3。

作业提交：
```js
var pi = 3.1415926
var area = r => pi * r * r;
```

## circum
原题：写一个函数，名字叫 circum。它的参数是 r，计算圆的周长。它可以和 area 共用一个变量 pi。

作业提交：
```js
var pi = 3.1415926
var circum = r => 2 * pi * r;
```

## innerArea

原题：写一个函数，名字叫 innerArea，它能计算下图中蓝色圆形的面积。innerArea 的输入是 a 和 b，输出是圆形的面积。 提示：\

- 这个题不需要用很聪明的办法做。你可以用 JavaScript 自带的函数 Math.sqrt 求平方根，比如 Math.sqrt(2) 就得到根号 2 的结果。
- 可以调用之前定义的 area 函数。
- 你可以在这个函数里面使用变量，用于简化表达式，并且避免重复计算。使用 function 的写法可以方便在函数内定义变量，因为花括号里面可以有多条语句。
- 两个参数之间的英文逗号后面要加个空格，不然就粘太近了。这跟英文写作的规则一样。
- 请注意函数名字的大小写规则。对于 JavaScript, Java 这类语言，函数一般以小写字母开头。如果名字多于一个英文单词，则后面的单词都用大写字母开头，但第一个单词仍然是小写。单词之间没有空格或者下划线。其它语言对此的规则可能会不同。这并不是很重要的事情，但为了工整美观，还是需要注
![[20210323210908856_7024.png]]

作业提交：
```js
//在浏览器console代码如下：
var pi = 3.14159;
function innerArea(a, b)
{
    var fc = (a,b) => Math.sqrt(a * a + b * b) / 2;
    var fs = r => pi * r * r;
    return fs(fc(a,b));
}
innerArea(3, 4);//19.6349375
```
![[20210323210943016_28693.png]]

【计算机科学家王垠老师ian】
这样重复计算太多了

【SeaflyWechat】
哦，好的，我再想想办法

【SeaflyWechat】
![[20210323211013552_4620.png]]

【计算机科学家王垠老师ian】
还没对

【SeaflyWechat】
我再检查检查

【SeaflyWechat】
![[20210323211034080_19686.png]]

【Super喵喵玄】
1.算半径这件事就做一次，也只有这个题目里用到了，没有必要创建一个函数，可以直接用表达式计算。
2.算圆面积的函数，抽出来是对的。其实按照题目顺序原本是先前在外面定义过 area 函数了，这里可以直接调用。

【SeaflyWechat】
哦，好的好的，还得看其他地方是否用到，用不到直接就在局部定义和计算。

【Super喵喵玄】
嗯嗯，如果发现重复用了再定义函数也不迟

## two
写一个函数 two，它接受一个函数 f 作为输入，返回一个新的函数。two(f) 会制造一个新的函数，它把 f 进行"双倍嵌套"。也就是说，如果新函数的参数叫 x，它会返回 f(f(x))。其中，f 是像 add1，square 那样的函数，接受一个参数。
![[20210323211116935_30921.png]]

举个例子：two(add1)(0)，相当于 add1(add1(0))，会返回 2。two(square)(3)，相当于 square(square(3))，会返回 81。

注意：这个 two 函数因为性质很特殊，为了方便将来的分析理解，请不要使用 function 的写法。请参考下面的模版，尽量保证示例结果是对的再发送。
```js
// 模板
var two = f => □;

// 示例 1
var add1 = x => x + 1;
var two_add1 = two(add1);
two_add1(0);    // 相当于 add1(add1(0))，结果是 2

// 示例 2
var square = x => x * x;
var two_square = two(square);
two_square(3);    // 相当于 square(square(3))，结果是 81
```

【SeaflyWechat】
two代码截图:
![[20210323211203017_25534.png]]

![[20210323211217432_2867.png]]

【SeaflyWechat】
这道题我做错了好多次。。。

【Super喵喵玄】
对的，思考过了效果肯定不一样

【SeaflyWechat】
two对函数的演变过程计算图草稿:
![[20210323211252752_32589.png]]

【SeaflyWechat】
two函数计算图和js代码:
![[20210323211316264_14657.png]]

## three, four
类似 two，写出 three 和 four。
```js
var three = f => □;
var four = f => □;

// 测试
three(x => x + 1)(0)    // 3
three(x => x * 2)(1)    // 8
four(x => x + 1)(0)     // 4
four(x => x * 2)(1)     // 16
```

【SeaflyWechat】
three_four_计算图草稿:
![[20210323211351144_1932.png]]

![[20210323211412320_11109.png]]

## succ
有了 two，three，four，我们想得到更多类似的函数，它们可以把函数 f 嵌套 5 次，6 次……

可是我们不想一个个定义这些函数。我们想定义一个函数 succ，它接受一个像 two 这样的函数 n，返回它的“下一个”（英文 successor）。

比如，succ(two) 会返回一个等价于 three 的函数，它会把它的输入 f 嵌套调用 3 次。

如果还看不明白，请看下面的例子。下面是 succ 的模板和示例：
```js
function succ(n)
{
    // ______
}

var three = succ(two);
var four = succ(three);
var five = succ(four);

// 结果示例：
var add1 = x => x + 1
two(add1)(0);     // 2
three(add1)(0);   // 3
four(add1)(0);    // 4
five(add1)(0);    // 5

// 注意这两个例子结果也必须对
three(x => x * 2)(1);  // 8
four(x => x * 2)(1);   // 16
```

提示：如果你卡住了实在做不出来，可以点击这里查看锦囊。

提示1：因为 succ(two) 会返回 three，所以我们大概知道 succ 返回的东西，肯定是类似 two, three 这样的「奇怪数」。因为 two，three 都是这样开头的：f => x => ... 所以 succ 返回的东西大概也应该是一样的开头方式。所以 succ 可以照这个模版来写：
```js
function succ(n)
{
  return f => x = > ...;
}
```

你只需要在省略号的地方填入内容就可以，是一个很短的表达式。

提示2：一个思路是把问题"实例化"，然后推广出通用的结果。比如，我们知道 succ(two) 会得到 three，也就是从 f => x => f(f(x))，succ 会给我们 f => x => f(f(f(x)))。所以好像可以试试如何从 f => x => f(f(x)) 得到 f(f(x)) （注意这两者的不同点），然后在 f(f(x)) 外面套一个 f(...)，得到 f(f(f(x)))。然后再从 f(f(f(x))) 得到 f => x => f(f(f(x)))。

提示3：这个提示仅当你卡在相关的地方，看了才会有意义。如果你的函数里有 n(f(x)) 这样的表达式，请思考一下，这里面 n 可能是 two，f 可能是 add1，而 x 可能是 0。所以 n(f(x)) 就可能是 two(add1(0))。two(add1(0)) 这个表达式有意义吗？

看看之前我们使用 two 的例子，具体是怎么写的。你会发现我们写的是 two(add1)(0)，而不是 two(add1(0))。two(add1(0)) 和 two(add1)(0) 有什么不同呢？如果你觉得它们没有什么不同，那你恐怕没有「按部就班」地按照课上教的思维方式去思考函数和调用。

下面这两个问题也许能帮助你：
two(add1(0)) 里面，two 的输入是什么？
two(add1)(0) 里面，two 的输入是什么？
两者有什么不同？

【SeaflyWechat】
succ计算图草稿:
![[20210323211505616_18970.png]]

【计算机科学家王垠老师ian】
提示一下：你的图基本是可以的，但是里面的 x 没有在任何地方写出来。

【SeaflyWechat】
哦，好的好的，我就是找不到出口了，所以想确认一下计算图本身有没有问题

【SeaflyWechat】
succ计算图推理图草稿图:
![[20210323211533592_27629.png]]

【SeaflyWechat】
老师您好，succ计算图推理我画出来了，但就是不知道怎么用代码来描述。。。

【SeaflyWechat】
陷入了一个非常尴尬的局面，就是我分析了前面的two和three、four之后，推理出了这张图，但就是不知道怎么用代码来描述这张计算图(突破这个瓶颈，后面相关的部分都能很快解决)
```js
var add1 = x => x + 1;
var two_add1 = x => add1(add1(x));
two_add1(0);//output:2
var two_add1 = f => x => f(f(x));
two_add1(add1)(0);//output:2

var three_add1 = x => add1(add1(add1(x)));
three_add1(0);//output:3
var three_add1 = f => x => f(f(f(x)));
three_add1(add1)(0);//output:3
```

![[20210323211605504_30351.png]]

```js
var two = f => (x => f(f(x)));
var succ = n => f => x=> f(n(f)(x));
succ(two)(add1)(0)//output:3
```

two计算图和代码运行截图:
![[20210323211641113_2184.png]]

【SeaflyWechat】
succ计算图和代码运行截图:
![[20210323211802128_30319.png]]

## 用 compose 表达 succ
课堂上讲的 compose 函数，可以帮助理解刚才写的 succ 函数。现在请用 compose 来表达 succ。"

compose 函数的定义如下：
```js
function compose(f, g)
{
  return x => f(g(x));
}
```

「用 compose 来表达 succ」的意思是：在 succ 的函数体里面调用 compose，用以代替 two 里面最关键的逻辑。举个例子：用 compose 来表达之前写的 two 函数，可以这样写：```var two = f => compose(f, f);```

仔细理解一下这个定义的意义，然后用 compose 来改写 succ。重新进行测试，保证结果正确。

提示：用 compose 改写之后，也许可以利用一个等价关系来简化它。如果 f 是一个单参数的函数，那么 x => f(x) 等价于 f。先想一下这是为什么？如果 f 是多参数的函数，也有类似的等价关系，比如 (x, y) => f(x, y) 等价于 f。不过也有可能你已经直接写出了最简的形式。

【SeaflyWechat】
```js
var compose = (f, g) => x => f(g(x));
var two = f => compose(f, f);
var succ = (n, f) => compose(n(f), f);
succ(two, add1)(0);//output:3
```

【Super喵喵玄】
succ 题目给出的模版只接受一个参数 n。

【SeaflyWechat】
好的，我马上修正一下：
```js
var compose = (f, g) => x => f(g(x));
var two = f => compose(f, f);
var succ = n => f => compose(n(f), f);
succ(two)(add1)(0);//output:3
```

【Super喵喵玄】
还不对，compose 接收函数是从右往左执行。

【SeaflyWechat】
好的，我马上修正一下：
```js
var compose = (f, g) => x => f(g(x));
var two = f => compose(f, f);
var succ = n => f => compose(f, n(f));//此处:n(f)计算结果传递给f
succ(two)(add1)(0);//output:3
```

【Super喵喵玄】
compose改写succ对了。

## toNumber
写一个函数 toNumber。这个函数接受一个像 two, tree, four 那样的函数 n，返回一个数字。这个数字表示这个 n 会把它的输入 f 重复多少次。

toNumber 的模板是这样：
```js
function toNumber(n)
{
    // ____
}
toNumber(two) //返回 2
toNumber(three) //返回 3
toNumber(four) //返回 4
//……
//以此类推。
```

【Super喵喵玄】
表达式可以直接返回，不需要变量。
```js
function toNumber(n)
{
    var num = n(add1)(0);
    return num;
}
toNumber(two);//output:2
toNumber(three);//output:3
```

【SeaflyWechat】
好的，我马上修正一下：
```js
function toNumber(n)
{
    return n(add1)(0);
}
toNumber(two);//output:2
toNumber(three);//output:3
```

【Super喵喵玄】
toNumber对了。

## zero

two, three, four, ... 这些函数很像自然数，对吧？现在请按照这个模式定义出 zero（零），然后用 succ 重新把 one, two, three, four, ..., nine 都定义出来，并且使用 toNumber 来验证它们确实表示了 0-9 这十个数。

【Super喵喵玄】
zero 不对，不能出现数字：
```js
var zero = f => x =>  0 * f(x);
var add1 = x => x + 1;
zero(add1)(0);//output:0
```

【SeaflyWechat】
好的，我马上修正一下：
```js
var zero = f => x => f(x);
var add0 = x => x + 0;
zero(add0)(0);//output:0
```

【Super喵喵玄】
zero 还是不对。

【SeaflyWechat】
好的，我再想想办法：
```js
var zero = f => x => f(x) - f(x);
zero(add1)(0);//output:0
```

【Super喵喵玄】
不是的，这里也不可以出现算数操作，比如你这里的减法。
two 是 f 嵌套 2 次, one 是 f 嵌套 1 次，你想想 zero 是 f 嵌套几次。

【SeaflyWechat】
额，嵌套0次，我再想想办法

```js
var zero = f => x => x;
zero(add1)(0);//output:0
```
zero、one、two计算图推演过程草稿图:
![[20210323212117416_21749.png]]

【Super喵喵玄】
对了。

【SeaflyWechat】
真不容易，，，表情_捂脸哭笑.png

【SeaflyWechat】
```js
var add1 = x => x + 1;
var zero = f => x => x;
zero(add1)(0);//output:0
toNumber(zero);//output:0

var one = f => x => f(zero(f)(x))
one(add1)(0);//output:1
toNumber(one);//output:1

var two = f => x => f(one(f)(x))
two(add1)(0);//output:2
toNumber(two);//output:2

var three = f => x => f(two(f)(x))
three(add1)(0);//output:3
toNumber(three);//output:3

var four = f => x => f(three(f)(x))
four(add1)(0);//output:4
toNumber(four);//output:4

//通过succ来生成其他数字函数
var succ = n => (f => (x => f(n(f)(x))));
succ(four)(add1)(0)//output:5

var five = succ(four);
var six = succ(five);
var seven = succ(six);
var eight = succ(seven);
var nine = succ(eight);

five(add1)(0);//output:5
six(add1)(0);//output:6
seven(add1)(0);//output:7
eight(add1)(0);//output:8
nine(add1)(0);//output:9

toNumber(five);//output:5
toNumber(six);//output:6
toNumber(seven);//output:7
toNumber(eight);//output:8
toNumber(nine);//output:9
```

## plus
我们好像真的可以把这些奇怪的函数 zero, one, two, three, ... 作为自然数对待。根据它们把函数 f 被嵌套的层数，它们似乎等价于 0, 1, 2, 3, ...

现在试试为这种「奇怪数」定义「加法」操作 plus。
```js
function plus(m, n)
{
  // ____
}

// 示例
toNumber(plus(two, three)) 会返回 5
toNumber(plus(five, six)) 会返回 11
```
注意：这是一个「只有函数」的世界。在 plus 和下面的 mult，pow，pred 等函数定义里，不能出现普通数字（0, 1, 2, ...），不能用 toNumber，不能用普通算术操作（+, -, ...）。想想为什么有这些限制，这其实不是我（或者任何人）定的规矩。不能用课上没讲过的概念（比如“递归”）。总之，只能用普通函数调用的方式实现。

【SeaflyWechat】
plus题提交如下：
```js
var plus = (m, n) => f => x => n(f)(m(f)(x));
toNumber(plus(two, three));//output:5
```

plus计算图原理: 例如,two的计算结果,传递给three,就实现了plus操作。

plus浏览器控制台代码运行效果截图:
![[20210323212248641_17822.png]]

【Super喵喵玄】
对的。

## 用 compose 表达 plus
类似于用 compose 表达 succ，现在请用 compose 来改写 plus。测试结果应该仍然正确。跟 succ 类似，同样要注意用「x => f(x) 等价于 f」来简化改写后的结果。

【SeaflyWechat】
用 compose 表达 plus题提交如下：
```js
var plus = (m, n) => f => compose(m(f), n(f));
toNumber(plus(two, three));//output:5
```
用compose表达plus代码运行效果图片:
![[20210323212329376_35.png]]

【Super喵喵玄】
对的。

## mult
为这种特别的「数」定义一个「乘法」操作 mult。注意：mult 的定义里请不要使用 plus。
```js
function mult(m, n)
{
  // ____
}

// 示例
toNumber(mult(two, three)) 会返回 6
toNumber(mult(five, six)) 会返回 30
```

![[d2430247a481a21a05f7f66d530951443283e1478806b4a0469b4a27dfc740f1.png]]  


【SeaflyWechat】
mult题提交如下：
![[20210323212402163_22403.png]]
```js
var mult = (m, n) => f => x => m(n(f))(x);
toNumber(mult(two, three));//output:6
```
【计算机科学家王垠老师ian】
可以简化

【SeaflyWechat】
var mult = (m, n) => f => x => m(n(f))(x);

【SeaflyWechat】
请问这还能简化吗？

【计算机科学家王垠老师ian】
可以的。提示里有一个等价关系可以用。

【SeaflyWechat】
好的好的，我想想办法

【SeaflyWechat】
```js
var mult = (m, n) => f => m(n(f));
toNumber(mult(two, three));//output:6
```

【计算机科学家王垠老师ian】
可以了。

【SeaflyWechat】
好的，我继续下一题

## 用 compose 表达 mult
请用 compose 来改写 mult，并尽量简化改写后的结果。测试结果应该仍然正确。跟 succ 和 plus 类似，同样注意用「x => f(x) 等价于 f」来简化改写后的结果。

提示：如果你发现不能简化，可以先改写成 var 的形式试试。

【SeaflyWechat】
用compose表达mult题提交如下
```js
var mult = (m, n) => f => compose(m(n(f)), zero(f));
toNumber(mult(two, three));//output:6
```

提示：如果你发现不能简化，可以先改写成 var 的形式试试。

【维加】
不对，太复杂了

【SeaflyWechat】
额，好的，我再想想办法

【个人感受】: 感觉老师们想尽办法封死你能想到的各种解题途径，挤压你的脑袋，让你想出更优质的解决办法，很nice，很刺激。

【SeaflyWechat】
根据compose计算图，不改动compose情况下，我现在想不出更简化的表达式了......
```js
var compose = (f, g) => x => f(g(x));
var mult = (m, n) => f => compose(m(n(f)), zero(f));
toNumber(mult(two, three));//output:6
```
【维加】
再多想一会吧

【SeaflyWechat】
好的，看来确实还有办法，我再找找办法。

```js
//简化后的表达式
var mult = (m, n) => f => m(compose(n(f), zero(f)));
toNumber(mult(two, three));//output:6
```

【计算机科学家王垠老师ian】
不对，这个等于做了一些无用功。

【SeaflyWechat】
哦，好的，我再想想办法

【SeaflyWechat】
```js
var mult = (m, n)
((m, n) => f => n(compose(m(f), zero(f))))(two, five)(add1)(0);//output:10
```

这个确实多了很多+0操作（无用功），但是我现在还没找到办法把这个+0操作去掉

【计算机科学家王垠老师ian】
不是去掉无用功的问题，而是你好像没有理解用 compose 的用意。

【计算机科学家王垠老师ian】
你这样硬塞一个 compose 进去，它其实没有起任何作用。

【计算机科学家王垠老师ian】
你关心的不应该是在某一个局部点，硬套一个 compose 进去，而是观察原来的代码，里面哪部分实质是在做 compose。然后把那部分用 compose 表达出来就行。

【计算机科学家王垠老师ian】
你的 succ 用 compose 都对了的，可以参考 succ 那个 compose 的用法。

【SeaflyWechat】
好，我再看看

【SeaflyWechat】
老师，这个我目前只能理解到这个程度......
脑袋不够用了[捂脸哭笑]

【计算机科学家王垠老师ian】
之前光是发图不说话，也不知道想表达什么。

【计算机科学家王垠老师ian】
不用太执着于图了，可以直接在代码上试试看。

【SeaflyWechat】
好的，我看看代码

【SeaflyWechat】
老师，做出来啦！

```js
var mult = (m, n) => compose(m, n);
toNumber(mult(three, four));//output:12
```

【SeaflyWechat】
我重新理解了一下compose到底是什么，然后代进去试了试，果然是这样的。

【SeaflyWechat】
我理解的compose：值传递，compose(f, g)；本质就是个值传递；只要g返回值和f输入值类型对应上就都适用。

【Super喵喵玄】
对的，但是还可以简化

【SeaflyWechat】
还能再简化？这也太神奇了！我再试试

【SeaflyWechat】
这......我能想到的简化就是删除分号了; [捂脸哭笑]

【计算机科学家王垠老师ian】
看一下题目里的提示

【SeaflyWechat】
好的好的

【SeaflyWechat】
```js
var mult = compose;
toNumber(mult(eight, five));//output:40
```
我的天呐！
老师你们太厉害了！

【个人感受】: 老师是真的把一些概念或者特性翻来覆去揉成一团之后，自由变换着千奇百怪的花样来考验你。他们不用担心这些花样会把他们自己整晕，因为他们掌握了这些概念或者特性的本质。

## pow
为「奇怪数」定义一个「幂」操作 pow，也就是求「m 的 n 次方」。注意：pow 的定义里请不要使用 plus 和 mult。
```js
function pow(m, n)
{
  // ____
}

// 示例
toNumber(pow(two, three)) 会返回 8
toNumber(pow(five, six)) 会返回 15625
```
思考：pow 可以用 compose 改写，或者用「x => f(x) 等价于 f」来简化吗？也许可以，也许不能。

【SeaflyWechat】
第pow题解答如下：
```js
var pow = (m, n) => f => n(m(m(f)));
toNumber(pow(two, four));//output:16
```

【计算机科学家王垠老师ian】
用其他数字试试呢

【SeaflyWechat】
额......其他数字试了，结果不对，我再想想。

【计算机科学家王垠老师ian】
可以试试不画图，直接单步替换看看。

【SeaflyWechat】
老师，pow我做出来啦！
没做出来原因还是因为没完全理解函数的输入和输出。 我之前pow的计算图都画出来了：
![[20210323212753576_30536.png]]

```js
function pow(m, n)
{
    return n(m);
}
show(toNumber(pow(two, three))); //会返回 8
show(toNumber(pow(three, four))); //会返回 81
show(toNumber(pow(five, six))); //会返回 15625
```

## pair
函数可以对数进行编码，还可以用来表达更复杂的数据结构(data structure)。所谓「数据结构」，就是内部包含多个组成部分的数据。就像汽车，是由很多部件组装在一起，每个部件都可以拆下来换掉。数据结构里面的组成部分，叫做它的成员（member）。

如果只有一个组成部分，就像 2，3 这些数一样，那就不叫"结构"了。我们把只有一个部分的数据，叫做原子数据(atom)，因为它好像不能拆分了，这就像科学家们曾经看待世界里的物质的方式一样。所以最小的数据结构，里面至少有两个组成部分，可以分别被拿出来。

有趣的是，我们其实不需要语言提供更多的功能，就能表达数据结构。我们可以利用函数来创造这样一种结构。我们可以把任意两个值 a 和 b 放进一个叫做二元组（pair）的结构。构造 pair 结构的函数可以这样定义：
```js
function pair(a, b)
{
  return select => select(a, b);
}

var p1 = pair(2, 3);  // 创造一个新的 pair 结构，内容是 2 和 3。
```
因为 pair 函数构造了一种新的数据结构，我们把它叫做构造函数(constructor)。构造函数在本质上只是一个普通的函数，给它一个特殊的称呼只是为了在叙述时提醒人们注意它的特殊用途。

我们来看看 pair 函数做了什么。这个构造函数 pair 接受参数 a 和 b，返回一个匿名函数 select => select(a, b)。这个匿名函数实现了「pair 结构」，因为它记住了 a 和 b（为什么？）。这个匿名函数本身可以被当作一个数据结构来用，它的参数 select 是一个「选择函数」。你可以自由地定义选择函数，把它交给 pair 作为输入。这样选择函数就会得到 a 和 b 作为参数，它就可以对 a 和 b 进行你希望的操作。

比如:
```js
var p1 = pair(2, 3);
p1((a, b) => a * b)  // 会返回 6
p1((a, b) => a + b)  // 会返回 5
```

现在请你定义两个函数 first 和 second，它们能分别取出这个 pair 结构的两个组成部分。当它们作用于一个 pair 的时候，能够分别得到它的第一和第二个成员。

first 和 second 的模版如下：
```js
function first(p)
{
  // 返回 p 的第 1 个元素 a
}

function second(p)
{
  // 返回 p 的第 2 个元素 b
}

// 示例
var p1 = pair(2, 3);
first(p1); // 2
second(p1); // 3

var p2 = pair(2, pair("你好", false));
first(p2); // 2
first(second(p2)); // "你好"
second(second(p2)); // false
```

老师提供的答案 + 自己思考：
```js
function pair(a, b)
{
  return select => select(a, b);
}
//我可以理解成如下：
var pair = (a, b) => f => f(a, b);

function first(p)
{
    return p((a, b)=> a);
}

function second(p)
{
    return p((a, b)=> b);
}

//我进一步得出下面表达式：
show(pair(3, 4)((a, b) => a * b));//12
```

## pred（很难）
写一个函数 pred，它是 succ 的相反操作。比如 succ(three) 得到 four，pred(four) 可以反过来得到 three。pred(zero) 没有定义，不会被用到，所以不用担心这个。
```js
function pred(n)
{
    // ____
}
```

注意：这是一个「只有函数」的世界。你的定义里不能出现普通数字(0, 1, 2, ...)，不能用 toNumber，不能用对普通数字的操作(+, -, ...)。不能用课上没讲过的概念，比如递归。总之，只能完全用函数调用的方式实现。不过你可以使用之前用函数定义的 succ，zero，pair 等。

这道题很难，但不会影响对之后课程内容的理解。如果一天还没想出来，可以暂时跳过，之后回头再来想想。课程进行期间不会公布这个题的答案。实际上这次的大部分练习只是为了加强对函数本质的理解，实际工作中是不会直接用这些函数的。

# 作业学生会议讨论

{}花括号,编程语言里面起到一种【语句块】的概念；

two(f)参数没传完这个认知是错误的，two是制造函数的函数，因为它需要的输入f，已经给了，然后它输出一个函数，它的使命完成了。

JavaScript在教学里只是工具，老师给我们讲的都是原理，思想。

console输入一个6，是一个表达式；回车后打印出6，是表达式的值。

two(f)是函数吗？这个要看哪个层面，在console输入这个的时候，它是一个表达式，这个表达式表达的是一个调用；回车后输出的是它的值。

表达式 到 值 之间的那个求值过程，叫做解释，即解释器。

one two three 的学名原来是奇怪数 我以为是自然数（：学名是 邱奇数

邓铭勇的问题：希望讲一下函数分析思路，目前我写的大部分是不断试出来的，而不是思考出来的。

想要表达自然数，需要零元（zero） 和单位元（one），所以如果只用函数定义自然数的话，函数体一定体现出某种计数的形式（比如说奇怪数的 f(f(x))）

单步替换，不是很明白单步替换具体要怎么做，怎么个替换法。比如f => x => f(f(x))，输入为f，是一个函数；输出为函数体；下图就是two(two(f))的单步替换计算图细节。
![[20210323212958882_13886.png]]

老师，我觉得 succ 函数的单步替换就挺有代表性的。

换着换着就绕晕了。

单步替换，只是老师为了帮助我们理解这个函数的用法而起的名字；实际的编译器或解释器并不是说先替换再替换。单步替换是一种思维的方法，实际上程序并不是这样运行的。

我们日常语言是知道输入，求输出；而Prolog(逻辑式语言)，可以反过来求输入。

函数实际上从一开头是单方向的，你这个反向操作都是怎么有这个想法的？

目前是没有一个很符合直觉的模型来描述的。

不是没有这样的需求，而是这个需求在实际上是很难实现的，因为要得到想要的结果，他所需要的计算量太大了；比如前面的Prolog实际上是穷举的。因为可能性太多了，运算量太大了，所以只有很简单的情况下才能得到结果，这就是为什么日本通过这种语言思想来做出人工智能语言失败的原因。

Fortran ==> Lisp

Lisp是世界上第2古老的语言，就是具有把函数作为输入。

f => x => f(n(f)(x));

【计算机科学家王垠老师ian】
我发现有同学因为以前学过的“形参”和“实参”这两个术语，导致了对函数的理解困难。我建议大家不要用“形参”和“实参”这样的术语，似乎是故意设计来让人糊涂的。以后对于术语我都尽量告诉大家英文的版本。

【计算机科学家王垠老师ian】
其实这两个东西，一个是榨汁机的输入管道的名字，一个是水果。叫他们“形参”和“实参”，因为这个“参”字，让人以为他们是同一类东西。

【计算机科学家王垠老师ian】
之前课程有同学每次都试图用他已经知道的“知识”来理解我讲的内容，结果遇到很大的困难。其实应该反过来：先忘记所有学过的东西，学了这里的内容，然后再拿去解释之前学过的东西。

【计算机科学家王垠老师ian】
很多时候我不告诉你们一些概念原来的名字就是这个原因，避免有同学上网去搜索，结果找到一些误导的材料。

【计算机科学家王垠老师ian】
术语不很重要。就算不知道别人叫它什么，也知道那是怎么回事。

【学员:melp】
是的，所以知道原来名字的同学，就不要说出来了。

【学员:邹邹邹邹】
嗯，虽然我有一定的编程知识，但是我在学习的时候都是在刻意忘记的情况下，尝试去理解老师说的内容，甚至有时会提出很“基础”的问题。

【学员:秋天的风】
对，希望已经有编程经验的同学，不要剧透，不要用老师还没讲过的知识。

【学员:melp】
之前所学和现在的计算机结构紧耦合，但是感觉王老师课上讲的内容会在一个更高的层面

【学员:melp】
如果能从这样一个更高的视角来理解现在甚至以后计算机的设计，真的是一件有意思的事情。期待接下来的课程。

【学员:佘一夫EF】
练习题我也觉得挺有意思，没有那么多的概念，真的是理解了才容易做出来

【学员:melp】
是的，仅仅通过函数，就能编码数字以及更复杂的数据结构，也是有点吃惊

【学员:秋天的风】
学完第一课我相信大家应该和我一样，发现了这个课的巨大魅力了。接下来就一起跟着老师一步一步的往下学。

【学员:melp】
宝藏课程

【计算机科学家王垠老师ian】
昨天有同学在 zoom 聊天里输入了 y = x + 2
这样的，说这是一个函数。当时忘了纠正。以后要避免使用 y = x + 2
这种形式来表示函数。这个是数学里面常见的错误的函数表示法。

【计算机科学家王垠老师ian】
1870年代的时候，有一个逻辑学家叫 Frege，专门写了论文纠正数学界的这种写法。
弗雷格
弗里德里希·路德维希·戈特洛布·弗雷格(德语:Friedrich Ludwig Gottlob Frege，1848年11月8日-1925年7月26日)，德国数学家、逻辑学家和哲学家。他是数理逻辑和分析哲学的奠基人，代表作为《概念演算--一种按算术语言构成的思维符号语言》。

【计算机科学家王垠老师ian】
他提出的正确写法，其实类似于我们教的这个写法： x => x + 2

【计算机科学家王垠老师ian】
只不过当时他是用图形的方式表达的，花了一根线来表示那个参数。

【计算机科学家王垠老师ian】
建议可以开始用 webstorm 之类的 IDE 了。

【学员:崮生】
可以用 vscode 吗

【计算机科学家王垠老师ian】
之后的练习再用 console 就不方便了
vscode 的 JavaScript 集成出了 bug。貌似还没好。不过你可以用它编辑，然后自己在 terminal 跑 node。

【计算机科学家王垠老师ian】
这个课不挑编辑器的。练习也都是抓图发，所以你能折腾好的环境就可以。

【计算机科学家王垠老师ian】
那种在线运行的网站也可以。比如 codesandbox.io

【学员:崮生】
推荐一个 js 在线运行的网站 https://www.typescriptlang.org/zh/play?noImplicitAny=false&useJavaScript=true#code/MYewdgziA2CmB00QHMAUBmAlEA


