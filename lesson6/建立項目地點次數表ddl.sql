-- public."114年定檢項目及金額" definition

-- Drop table

-- DROP TABLE public."114年定檢項目及金額";

CREATE TABLE public."114年定檢項目及金額" (
	項次 int4 NULL,
	項目 varchar(50) NULL,
	單價 int4 NULL,
	CONSTRAINT "114年定檢項目及金額_pkey" PRIMARY KEY ("項目")
);


-- public."114年定檢項目地點及次數" definition

-- Drop table

-- DROP TABLE public."114年定檢項目地點及次數";

CREATE TABLE public."114年定檢項目地點及次數" (
	項目 varchar(50) NULL,
	第1季 int4 NULL,
	第2季 int4 NULL,
	"第3季-1" int4 NULL,
	"第3季-2" int4 NULL,
	"第4季-1" int4 NULL,
	"第4季-2" int4 NULL,
	地點 varchar(50) NULL,
	CONSTRAINT "114年定檢項目地點及次數_項目_fkey" FOREIGN KEY (項目) REFERENCES public."114年定檢項目及金額"(項目)
);